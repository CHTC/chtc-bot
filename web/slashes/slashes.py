from flask import Blueprint

slash_bp = Blueprint("slash", __name__)


def slash_command(command):
    def _(func):
        return slash_bp.route(f"/slash/{command}", methods=["POST"])(func)

    return _
