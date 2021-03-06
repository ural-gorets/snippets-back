import json
import math
from datetime import datetime
from hashlib import md5
import requests as req

from flask import request
import aiohttp
import asyncio
from flask_restful import Resource, reqparse
from flask_api import status

from guesslang import Guess

import models
from run import db    # "func" inside db object


class Wall(Resource):
    """
    Returns snippets list for one specified page.
    snippets for answer defined in query string of request as ?page=X.
    """
    def get(self):
        # make request to base for rows number
        rows = db.session.query(models.Snippets.id).filter(models.Snippets.public_flag).count()
        snipp_on_page = 2    # Snippets number on one page
        pages = rows//snipp_on_page + math.ceil(rows/snipp_on_page - rows//snipp_on_page)

        # get page number from request
        page_number = int(request.args.get('page')) if request.args.get('page') else 1

        # make request for snippets list for current page and sort data.
        snippets_list = db.session.query(models.Snippets)\
            .filter(models.Snippets.public_flag)\
            .order_by(models.Snippets.born_date.desc())\
            .offset((page_number-1)*snipp_on_page).limit(snipp_on_page)\
            .all()

        # gets LangStat table
        LangStat = db.session.query(models.LangStat).all()

        # make response object and return it.
        answer = {"pages": pages, "allowed_languages": Upload.allowed_langs}
        # adds languages statistics
        langstat = {}
        for lang in LangStat:
            langstat[lang.language] = {"amount": lang.fragments_counter,
                                      "percent": lang.fragments_percent, }
        answer["languages"] = langstat
        # adds snippets info
        snippets = {}
        for snippet in snippets_list:
            snippets[snippet.name] = {
                "id": snippet.id,
                # "name": snippet.name,
                "description": snippet.description,
                "reference": "/show/{}".format(snippet.reference),
                "preview": snippet.preview,
                "date": "{}".format(snippet.born_date),
            }
        answer["snippets"] = snippets
        j_answer = json.dumps(answer)

        return j_answer


class Snippet(Resource):
    """
    Returns all data of specified snippet.
    """
    def get(self, snippet_ref):
        # make request for whole snippet with all data
        request_res = db.session.query(models.Snippets, models.Files) \
            .outerjoin(models.Files) \
            .filter(models.Snippets.reference == snippet_ref) \
            .all()

        # request result looks like this:
        #  list with "sqlalchemy.util._collections.result" objects
        # (<Snippets>, <Files>), but Files field may be "None" if there no files
        # at all for this snippet.
        #
        # [(<Snippets 4>, <Files 4>),
        # (<Snippets 4>, <Files 3>),
        # (<Snippets 4>, <Files 2>)]
        #
        # Accessing value of some field may be done like this:
        # request_res[0].Snippets.name
        # request_res[2].Files.data
        #
        # if snippet's name incorrect, and nothing found in database, list will be empty. request_res == []

        # add all snippet's fields to the answer and send it
        answer = {}
        if request_res:
            snippet = {}
            snippet["name"] = request_res[0].Snippets.name
            snippet["description"] = request_res[0].Snippets.description
            snippet["born_date"] = "{}".format(request_res[0].Snippets.born_date)
            snippet["public_flag"] = request_res[0].Snippets.public_flag
            answer["snippet"] = snippet

            files = {}
            for req in request_res:
                file = {}
                if req.Files:
                    file["name"] = req.Files.filename
                    file["type"] = req.Files.type
                    file["lang"] = req.Files.lang
                    file["data"] = req.Files.data
                else:
                    file["name"] = "No files"
                    file["data"] = "Something goes wrong, and there no any data."
                files[file['name']] = file
            answer["files"] = files
        else:
            answer ={"message": "Seems, reference incorrect."}

        j_answer = json.dumps(answer)
        return j_answer


class Upload(Resource):
    """
    Handle uploaded snippet, add it to the database.
    """
    allowed_langs = ['Python', 'Javascript', 'Perl', 'Ruby', 'Shell',
                     'HTML', 'CSS', 'SQL', 'PHP', 'Другой']

    def post(self):
        # Extract FormData keys.
        form_keys = list(request.form.keys())

        # Select Max id value from snippets table
        max_snippets_id = db.session.query(db.func.max(models.Snippets.id)).scalar()
        new_snippet_id = max_snippets_id + 1 if max_snippets_id else 1

        # create record in 'snippets' table.
        snippet_info = json.loads(request.form['info'])
        reference = md5(bytes(snippet_info['name'], encoding='utf-8')).hexdigest()
        try:
            new_snippet = models.Snippets(
                name=snippet_info['name'],
                id=new_snippet_id,
                public_flag=snippet_info['public_flag'],
                reference=reference,
                description=snippet_info['description'],
                born_date=datetime.now(),
                preview='default',                          # ADD HERE FIRST 10 ROWS FROM FIRST FILE
            )
            models.save_to_db(db, new_snippet, 'add')

        except Exception as err:
            print('Exception: ', err, '\n#############################')
            answer = {"message": "snippet saving error: {}".format(err)}
            return answer, status.HTTP_500_INTERNAL_SERVER_ERROR

        # Presence of some data was checked in front, so here no need to do it.
        # Puts data to database and return error message if problems.
        if_not_saved = self.data_to_db(form_keys, new_snippet_id, new_snippet.public_flag)
        if if_not_saved:
            return if_not_saved, status.HTTP_500_INTERNAL_SERVER_ERROR

        # Create 'prewiew' text for snippet from saved data.
        preview_not_created = self.create_preview(new_snippet_id)
        if preview_not_created:
            return preview_not_created, status.HTTP_500_INTERNAL_SERVER_ERROR

        answer = {"message": "Snippet successfully created.",
                "reference": reference}
        j_answer = json.dumps(answer)
        return j_answer, status.HTTP_201_CREATED

    
    async def get_reference(self, ref):
        """
        Asynchronous URL checking function. Returns dict with fields:
        "status": int, HTTP status code or None if server inaccessible.
        "reference": string, reference.
        "data": string, fragment text if status is 200,
        otherwise - dict {"message": "error message"}.
        """
        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # For first performs HEAD request and check file length.
                async with session.head(ref) as resp:
                    if resp.status == 200:
                        if int(resp.headers['Content-Length']) > 1048576:
                            return {"status": 403, "data": {"message": "Too big data."}, "reference": ref}

                        # If file length is ok, performs GET request.
                        async with session.get(ref) as response:
                            if response.status == 200:
                                # response.text() is corutine, so await is required.
                                return {"status": 200, "data": await response.text(encoding='utf-8'), "reference": ref}
                            else:
                                return {"status": response.status, "reference": ref, "data":\
                                       {"message": "URL not accessible. Status code is {}".format(response.status)}}
                    else:
                        return {"status": resp.status, "reference": ref, "data":\
                               {"message": "URL not accessible. Status code is {}".format(resp.status)}}
        except Exception as err:
            return {"status": None, "reference": ref, "data":\
                   {"message": "No response from the server. {}".format(err)}}

    def data_to_db(self, form_keys, new_snippet_id, public_flag):
        try:
            # If files data presents, create record in 'files' table.
            if 'files' in form_keys:
                files = json.loads(request.form['files'])
                files_names = files.keys()
                for name in files_names:
                    # checks language field and detect if empty.
                    language = files[name]['language'] if files[name]['language'] \
                        else self.detect_language(files[name]['content'])
                    # creates new record object and save it to db.
                    new_file = models.Files(
                        snippets_id=new_snippet_id,
                        filename=name,
                        type='file',
                        lang=language,
                        data=files[name]['content'],
                    )
                    models.save_to_db(db, new_file, 'add')

                    # if snippet public, update language statistics.
                    if public_flag:
                        lang_stat_not_updated = self.update_lang_stat(language)
                        if lang_stat_not_updated:
                            return lang_stat_not_updated     # RAISE ERROR INSTEAD

            # If text_form data presents, create record in 'files' table.
            if 'text' in form_keys:
                texts = json.loads(request.form['text'])
                texts_titles = texts.keys()
                for title in texts_titles:
                    # checks language field and detect if empty.
                    language = texts[title]['language'] if texts[title]['language'] \
                        else self.detect_language(texts[title]['content'])
                    # creates new record object and save it to db.
                    new_file = models.Files(
                        snippets_id=new_snippet_id,
                        filename=title,
                        type='text_form',
                        lang=language,
                        data=texts[title]['content'],
                    )
                    models.save_to_db(db, new_file, 'add')
                    if public_flag:
                        lang_stat_not_updated = self.update_lang_stat(language)
                        if lang_stat_not_updated:
                            return lang_stat_not_updated    # RAISE ERROR INSTEAD

            # If references data presents, create record in 'files' table.
            if 'refs' in form_keys:
                refs = json.loads(request.form['refs'])
                references = list(refs.keys())

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                tasks = [self.get_reference(ref) for ref in references]
                fut = asyncio.gather(*tasks, return_exceptions=True)
                loop.run_until_complete(fut)
                
                fut_result = fut.result()
                inaccessible = []
                for answer in fut_result:
                    # answer is a dict returned by "get_reference" function.
                    if answer["status"] != 200:
                        inaccessible.append(answer['reference'])

                if inaccessible:
                    self.cancel_transaction(new_snippet_id)
                    insertion = ""
                    for item in inaccessible:
                        print('\nitem: ', item)
                        insertion += "{}; ".format(item)
                    return {"message": "Problems with URL: {}. Transaction cancelled.".format(insertion)}

                for num in range(len(fut_result)):
                    # checks language field and detect if empty.
                    language = refs[references[num]] if refs[references[num]] \
                        else self.detect_language(fut_result[num]["data"])    # file_request.content.decode('utf-8'))
                    # save data to database
                    new_file = models.Files(
                        snippets_id=new_snippet_id,
                        filename=references[num],
                        type='reference',
                        lang=language,
                        data=fut_result[num]["data"],
                    )
                    models.save_to_db(db, new_file, 'add')
                    if public_flag:
                        lang_stat_not_updated = self.update_lang_stat(language)
                        if lang_stat_not_updated:
                            return lang_stat_not_updated   # RAISE ERROR INSTEAD

                loop.close()

        except Exception as err:
            print('Exception in "data_to_db": ', err, '\n#############################')
            answer = {"message": "data saving error: {}".format(err)}
            self.cancel_transaction(new_snippet_id)
            return answer, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def update_lang_stat(language):
        try:
            # Looking for record with stats for language. None if absent.
            record = db.session.query(models.LangStat).filter(models.LangStat.language == language).first()

            # Change fragments amount or create new record if absent.
            if record:
                record.fragments_counter += 1
                # record.fragments_percent = 0    # record.fragments_counter*100/(summ+1)
                db.session.commit()
            else:
                new_record = models.LangStat(
                    language=language,
                    fragments_counter=1,
                    fragments_percent=0    #100/(summ+1)
                )
                models.save_to_db(db, new_record, "add")

            # Recounts % for all languages with changed total fragments amount.
            # Sum the number of all code fragments in all records.
            summ = db.session.query(db.func.sum(models.LangStat.fragments_counter)).scalar()
            # Gets all records from table
            LangStat = db.session.query(models.LangStat).all()
            # and iterates by them.
            for obj in LangStat:
                obj.fragments_percent = obj.fragments_counter * 100 / summ
                db.session.commit()
        except Exception as err:
            print('Exception: ', err, '\n#############################')
            answer = {"message": "snippet deleting error: {}".format(err)}
            return answer, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def create_preview(snippet_id):
        try:
            for_preview = db.session.query(models.Files.data).filter(models.Files.snippets_id == snippet_id).first()[0]
            preview = ''
            for i in range(10):
                fragments = for_preview.partition('\n')
                preview += fragments[0] + fragments[1]
                for_preview = fragments[2]

            snippet = models.Snippets.find_by_id(snippet_id)
            snippet.preview = preview
            db.session.commit()
        except Exception as err:
            print('Exception: ', err, '\n#############################')
            answer = {"message": "Preview creation error: {}".format(err)}
            self.cancel_transaction(snippet_id)
            return answer, status.HTTP_500_INTERNAL_SERVER_ERROR

    @staticmethod
    def cancel_transaction(id_value):
        try:
            # select from snippets
            rows_to_delete = db.session.query(models.Snippets).filter(models.Snippets.id == id_value).all()
            # select from files
            rows_to_delete += db.session.query(models.Files).filter(models.Files.snippets_id == id_value)
            print('These rows are to delete: ', rows_to_delete)

            for obj in rows_to_delete:
                models.save_to_db(db, obj, 'delete')

        except Exception as err:
            print('Exception: ', err, '\n#############################')
            answer = {"message": "snippet deleting error: {}".format(err)}
            return answer, status.HTTP_500_INTERNAL_SERVER_ERROR

    @classmethod
    def detect_language(cls, text):
        lang = Guess().language_name(text)
        return lang if lang in cls.allowed_langs else 'Другой'


class Test(Resource):
    def get(self):
        # Now testing asyncrinous request for url
        answer = []
        form_keys = list(request.form.keys())
        for key in form_keys:
            print('Sending request for: ', request.form[key])
            
        # files = json.loads(request.form['files'])


        # ans = []
        # summ = db.session.query(db.func.sum(models.LangStat.fragments_counter)).scalar()
        # LS = db.session.query(models.LangStat).all()
        # for obj in LS:
        #     percent = obj.fragments_counter * 100/summ
        #     ans.append(percent)
        # answer = {"message": "request result is {}.".format(ans)}
        
        j_answer = json.dumps(answer)
        return j_answer
