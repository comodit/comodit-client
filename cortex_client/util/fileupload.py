import mimetypes, pycurl

class PyCurlCallBack(object):
    def __init__(self):
        self.response = ''

    def response_callback(self, response):
        self.response += response

def post_multipart(host, selector, fields, files, headers = {}):
    c = pycurl.Curl()
    c.setopt(c.POST, 1)
    c.setopt(c.URL, str("http://" + host + selector))

    # Build header
    curl_headers = []
    for key in headers:
        curl_headers.append(key + ":" + headers[key])
    c.setopt(c.HTTPHEADER, curl_headers)

    # Add data
    for (key, value) in fields:
        c.setopt(c.HTTPPOST, [(key, value)])

    # Add files
    curl_files = []
    for (key, filename) in files:
        curl_files.append((key, (c.FORM_FILE, str(filename))))
    c.setopt(c.HTTPPOST, curl_files)

    # Set callback
    callback = PyCurlCallBack()
    c.setopt(c.WRITEFUNCTION, callback.response_callback)

    c.perform()
    c.close()

    return callback.response

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
