
from django.core.files.uploadhandler import StopUpload

from anime.tests._classes import CleanTestCase as TestCase
from anime.upload import QuotaUploadHandler


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
