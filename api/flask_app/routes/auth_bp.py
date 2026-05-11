import secrets
from flask import Blueprint, redirect, request, session, current_app, jsonify
from core.line_api import exchange_code_for_token, get_line_profile
from api.flask_app.models import User

auth_bp = Blueprint('auth_bp', __name__)

_LINE_AUTH_URL = "https://access.line.me/oauth2/v2.1/authorize"


@auth_bp.route("/auth/line")
def line_login():
    state = secrets.token_urlsafe(16)
    session['oauth_state'] = state
    params = (
        f"?response_type=code"
        f"&client_id={current_app.config['LINE_LOGIN_CHANNEL_ID']}"
        f"&redirect_uri={current_app.config['LINE_LOGIN_REDIRECT_URI']}"
        f"&scope=profile"
        f"&state={state}"
    )
    return redirect(_LINE_AUTH_URL + params)


@auth_bp.route("/auth/line/callback")
def line_callback():
    if request.args.get('state') != session.pop('oauth_state', None):
        return jsonify({'error': 'Invalid state'}), 400

    code = request.args.get('code')
    if not code:
        return jsonify({'error': 'Missing code'}), 400

    try:
        access_token = exchange_code_for_token(
            code=code,
            redirect_uri=current_app.config['LINE_LOGIN_REDIRECT_URI'],
            client_id=current_app.config['LINE_LOGIN_CHANNEL_ID'],
            client_secret=current_app.config['LINE_LOGIN_CHANNEL_SECRET'],
        )
        profile = get_line_profile(access_token)
    except Exception as e:
        current_app.logger.error(f"LINE Login failed: {e}")
        return jsonify({'error': 'LINE 登入失敗，請稍後再試。'}), 502

    user_id = profile['userId']
    if not User.exists(user_id):
        User.create(user_id)

    session['user_id'] = user_id
    session['display_name'] = profile.get('displayName', '')
    return redirect(current_app.config['FRONTEND_URL'])


@auth_bp.route("/auth/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({'ok': True})


@auth_bp.route("/auth/me")
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'logged_in': False})
    return jsonify({
        'logged_in': True,
        'user_id': user_id,
        'display_name': session.get('display_name'),
    })
