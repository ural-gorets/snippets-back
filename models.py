from run import db

class LangStat(db.Model):
    __tablename__ = 'langstat'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    language = db.Column(db.String())
    fragments_counter = db.Column(db.Integer())
    fragments_percent = db.Column(db.Float())


class Snippets(db.Model):
    __tablename__ = 'snippets'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False, unique=True)
    public_flag = db.Column(db.Boolean, nullable=False)
    reference = db.Column(db.String(), nullable=False)
    description = db.Column(db.Text, nullable=False)
    preview = db.Column(db.Text, nullable=False)
    born_date = db.Column(db.DateTime())

    children_files = db.relationship('Files', cascade='all, delete', backref='snippets')

    @classmethod
    def find_by_name(cls, snippet_name):
        return cls.query.filter_by(name=snippet_name).first()

    @classmethod
    def find_by_id(cls, snippet_id):
        return cls.query.filter_by(id=snippet_id).first()


class Files(db.Model):
    """
    <type> can be one of these: file, text_form, reference.
    """
    __tablename__ = 'files'

    id = db.Column(db.Integer, nullable=False, primary_key=True, autoincrement=True)
    snippets_id = db.Column(db.Integer, db.ForeignKey('snippets.id'), nullable=False)
    filename = db.Column(db.String(), nullable=False)
    type = db.Column(db.String())
    lang = db.Column(db.String())
    data = db.Column(db.Text)


def save_to_db(db, table_class, method="add"):
    """
    This function saves changes to database. It can add or delete data.
    :param db: database object where to save;
    :param table_class: Table object to add or delete;
    :param method: "add" or "delete" method. By default method = "add".
    """
    if method == "add":
        db.session.add(table_class)
    elif method == "delete":
        db.session.delete(table_class)

    db.session.commit()

