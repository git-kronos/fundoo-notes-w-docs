from functools import wraps

from django.db import connection, transaction
from django.http.request import QueryDict
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response

from apps.utils import JwtAuthentication


# Create your views here.
@transaction.atomic
def custom_sql(sql: str, param: dict | None = None, many: bool = False, serialize=True):
    def _serialize(cursor):
        columns = [col[0] for col in cursor.description]
        if not many:
            data = cursor.fetchone()
            return dict(zip(columns, data)) if data else None
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    with connection.cursor() as cursor:
        cursor.execute(sql, param)
        return None if not serialize else _serialize(cursor)


def update_user_input(f):
    @wraps(f)
    def wrapper(request, *a, **kw):
        if isinstance(request.data, QueryDict):
            request.data._mutable = True
            request.data.appendlist("owner", request.user.id)
            request.data._mutable = False
        elif isinstance(request.data, dict):
            request.data["owner"] = request.user.id
        return f(request, *a, **kw)

    return wrapper


class NoteCRUD:
    _SELECT_QUERY_LIST = """
    SELECT
        n.id, n.title, n.body,
        _user.first_name || ' ' || _user.last_name as "owner",
        ARRAY (
            SELECT
                _user.first_name || ' ' || _user.last_name
            FROM
                note_collaborator nc
            LEFT JOIN user_user _user ON nc.user_id = _user.id
            WHERE
                nc.note_id = n.id) AS collaborator
        FROM
            note n LEFT JOIN user_user _user ON n.owner_id = _user.id
        WHERE
            owner_id = %(owner_id)s
            OR %(owner_id)s = ANY (ARRAY (
                    SELECT
                        nc.user_id
                    FROM
                        note_collaborator nc
                    WHERE
                        nc.note_id = n.id))
            ORDER BY
                n.id DESC;
    """
    _SELECT_QUERY_RETRIEVE = """
SELECT
	n.id,
	n.title,
	n.body,
	_user.first_name || ' ' || _user.last_name AS "owner",
	ARRAY (
		SELECT
			_user.first_name || ' ' || _user.last_name
		FROM
			note_collaborator nc
		LEFT JOIN user_user _user ON nc.user_id = _user.id
	WHERE
		nc.note_id = n.id) AS collaborator
FROM
	note n
	LEFT JOIN user_user _user ON n.owner_id = _user.id
WHERE (n.id = %(pk)s)
	AND(n.owner_id = %(owner_id)s
		OR %(owner_id)s = ANY (ARRAY (
				SELECT
					user_id FROM note_collaborator nc
				WHERE
					nc.note_id = n.id)));
    """
    _UPDATE_QUERY = """
UPDATE
	note n
SET
	title = %(title)s,
	body = %(body)s
WHERE ( n.id = %(pk)s )
	AND(n.owner_id = %(owner_id)s
		OR %(owner_id)s = ANY (ARRAY (
				SELECT
					user_id FROM note_collaborator nc
				WHERE
					nc.note_id = n.id)))
RETURNING
	*;
"""

    @classmethod
    def list(cls, user_id):
        return custom_sql(sql=cls._SELECT_QUERY_LIST, param={"owner_id": user_id}, many=True), 200

    @classmethod
    def retrieve(cls, owner_id, pk):
        result = custom_sql(sql=cls._SELECT_QUERY_RETRIEVE, param={"owner_id": owner_id, "pk": pk})
        return (result, 200) if result else ({"message": "Note not found"}, 404)

    @staticmethod
    def create(data):
        query = "insert into note (title, body, owner_id) values (%(title)s, %(body)s, %(owner)s) RETURNING *"
        return custom_sql(sql=query, param=data), 201

    @staticmethod
    def destroy(owner_id, pk):
        query = """
        DELETE FROM note_collaborator WHERE note_id=%(pk)s;
        DELETE FROM note WHERE owner_id = %(owner_id)s and id=%(pk)s;
        """
        return custom_sql(sql=query, param={"owner_id": owner_id, "pk": pk}, serialize=False), 204

    @classmethod
    def update(cls, owner_id, pk, payload):
        return custom_sql(sql=cls._UPDATE_QUERY, param={"owner_id": owner_id, "pk": pk, **payload}), 202


@api_view(["GET", "POST"])
@authentication_classes([JwtAuthentication])
@update_user_input
def list_note(request):
    if request.method == "POST":
        return Response(*NoteCRUD.create(request.data))
    return Response(*NoteCRUD.list(user_id=request.user.id))


@api_view(["GET", "PUT", "DELETE"])
@authentication_classes([JwtAuthentication])
@update_user_input
def detail_note(request, pk=None):
    if request.method == "DELETE":
        return Response(*NoteCRUD.destroy(owner_id=request.user.pk, pk=pk))
    elif request.method == "PUT":
        return Response(*NoteCRUD.update(owner_id=request.user.pk, pk=pk, payload=request.data))
    return Response(*NoteCRUD.retrieve(request.user.pk, pk))
