from flask import Blueprint, render_template, make_response, jsonify, redirect, url_for

from flask_jwt_extended import create_access_token, set_access_cookies, get_jwt_identity, jwt_required

foldername = 'q3'

# Blueprint Configuration
q3_bp = Blueprint(
    'q3_bp', __name__,
    url_prefix=f'/{foldername}',
    template_folder='templates',
    static_url_path="/static"
)


@q3_bp.route("/login", methods=["GET"])
def login():
    username = 'anonymous'
    access_token = create_access_token(identity=username)
    resp = jsonify({'login': True})
    set_access_cookies(resp, access_token)
    return resp, 200


@q3_bp.route("/flag", methods=["GET"])
@jwt_required(optional=True)
def protected():
    current_identity = get_jwt_identity()

    if current_identity == 'admin':
        indexmd = open(f"{bp_dir}/md/flag", "r").read()
        resp = make_response(render_template('blank.html', data=indexmd))
        return resp, 200
    elif current_identity == 'anonymous':
        data = 'No No No!!! - This is super-secret'
        resp = make_response(render_template('blank.html', data=data))
        return resp, 404
    else:
        return redirect(url_for('q3_bp.login'))


@q3_bp.route('/', defaults={'u_path': 'index'})
@q3_bp.route('/<path:u_path>')
@jwt_required(optional=True)
def index(u_path):
    current_identity = get_jwt_identity()
    logger.info(current_identity)
    if current_identity is not None:
        try:
            indexmd = open(f"{bp_dir}/md/{u_path}", "r").read()
        except Exception as e:
            return render_template('blank.html', data='oops page not found!!!')
        resp = make_response(render_template('blank.html', data=indexmd))
        return resp
    else:
        return redirect(url_for('q3_bp.login'))
