
from django.core.files.uploadhandler import StopUpload

from anime.tests._classes import CleanTestCase as TestCase
from anime.upload import QuotaUploadHandler

#~ import base64
#~ from django.utils.encoding import force_bytes
#~ from django.test import client


class UploadTest(TestCase):

    def test_QuotaUploadHandler(self):
        uh = QuotaUploadHandler()
        uh.file = open('/dev/null', 'w')
        with open('/dev/zero', 'r') as fl:
            size = 0
            count = 2 ** 20
            while size < uh.QUOTA * 2:
                chunk = fl.read(count)
                try:
                    uh.receive_data_chunk(chunk, None)
                except StopUpload:
                    break
                size += count
                assert size < uh.QUOTA
        uh.file.close()

    #~ Ticket #19036
    #~ def test_base64_upload(self):
        #~ test_string = open('/dev/urandom', 'r').read(524288)
        #~ payload = "\r\n".join([
            #~ '--' + client.BOUNDARY,
            #~ 'Content-Disposition: form-data; name="file"; filename="test.txt"',
            #~ 'Content-Type: application/octet-stream',
            #~ 'Content-Transfer-Encoding: base64',
            #~ '',
            #~ base64.b64encode(force_bytes(test_string)).decode('ascii'),
            #~ '--' + client.BOUNDARY + '--',
            #~ '',
        #~ ]).encode('utf-8')
        #~ r = {
            #~ 'CONTENT_LENGTH': len(payload),
            #~ 'CONTENT_TYPE':   client.MULTIPART_CONTENT,
            #~ 'PATH_INFO':      "/file_uploads/echo_content/",
            #~ 'REQUEST_METHOD': 'POST',
            #~ 'wsgi.input':     client.FakePayload(payload),
        #~ }
        #~ response = self.client.request(**r)
        #~ received = json.loads(response.content.decode('utf-8'))
#~
        #~ self.assertEqual(received['file'], test_string)