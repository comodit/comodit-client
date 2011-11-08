import httplib, mimetypes, pycurl

def post_multipart(host, selector, fields, files, headers = {}):
    return post_multipart_httplib(host, selector, fields, files, headers)

class PyCurlCallBack(object):
    def __init__(self):
        self.response = ''

    def response_callback(self, response):
        self.response += response

def post_multipart_pycurl(host, selector, fields, files, headers = {}):
    c = pycurl.Curl()
    c.setopt(c.POST, 1)
    c.setopt(c.URL, host + "/" + selector)

    # Build header
    curl_headers = []
    for key in headers:
        curl_headers.append(key + ":" + headers[key])
    c.setopt(c.HTTPHEADER, curl_headers)

    # Add data
#    for (key, value) in fields:
#        c.setopt(c.HTTPPOST, [(key, (c.FORM_DATA, value))])

    # Add files
    curl_files = []
    for (key, filename, value) in files:
        curl_files.append((key, (c.FORM_FILE, filename)))
    c.setopt(c.HTTPPOST, curl_files)

    # Set callback
    callback = PyCurlCallBack()
    c.setopt(c.WRITEFUNCTION, callback.response_callback)

    c.setopt(c.VERBOSE, 1)
    c.perform()
    c.close()

    return callback.response

def post_multipart_httplib(host, selector, fields, files, headers = {}):
    """
    Post fields and files to an http host as multipart/form-data.
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return the server's response page.
    """
    content_type, body = encode_multipart_formdata(fields, files)
    h = httplib.HTTP(host)
    h.putrequest('POST', selector)
    h.putheader('content-type', content_type)
    h.putheader('content-length', str(len(body)))
    for key in headers:
        h.putheader(key, headers[key])
    h.endheaders()
    h.send(body)
    errcode, errmsg, headers = h.getreply()
    return h.file.read()

def encode_multipart_formdata(fields, files):
    """
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    """
    BOUNDARY = '----------ThIs_Is_tHe_bouNdaRY_$'
    CRLF = "\r\n"
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value.decode('string_escape'))
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        content_type = get_content_type(filename)
        L.append('Content-Type: %s' % content_type)
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join([element.decode('string_escape') for element in L])
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
