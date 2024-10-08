from flask import request, jsonify, redirect
from app import app
from app.logger import logger
from app.url_validator import is_valid_url
from app.url_processor import create_and_store_hash, get_url_for_hash

@app.before_request
def log_request_info():
    logger.info('Headers: %s', request.headers)
    logger.info('Body: %s', request.get_data())

@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    '''
    The expected request format: {"url": "https://www.google.com/long/path?with=query"}
    Responds with: {"short_url": "https://domain.com/3P4ykvA9"}
    '''
    content = request.json
    url = content.get('url')
    if url is None:
        return _error_response('No URL provided', 400)
    elif not is_valid_url(url):
        return _error_response("The provided URL is not valid. Please provide a URL in the format: http://www.example.com", 400)
    else:
        url_hash = create_and_store_hash(url)
        response_body = {
            "short_url": f"{request.host_url}{url_hash}"
        }
        return jsonify(response_body), 200
    
@app.route('/<url_hash>', methods=['GET'])
def open_url_for_hash(url_hash):
    url = get_url_for_hash(url_hash)
    if (url is None):
        return _error_response("URL not found", 404)
    else:
        return redirect(location=url, code=302)
    
def _error_response(error_message: str, error_code: int):
    response_body = {
        "error_message": error_message
    }
    return jsonify(response_body), error_code
