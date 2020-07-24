import json
import logging
import requests


class Email():
    def __init__(self, to, subject, message, name="Data") -> None:
        self._to = to
        self._name = name
        self._subject = subject
        self._message = message
        self.log = logging.getLogger('email')

    def attach(self, filename, binary, file_type):
        # pylint: disable-all
        self._filename = filename
        self._binary = binary
        self._file_type = file_type
        self.to_attach = True

    def headers(self):
        return {"Content-Type": "application/x-www-form-urlencoded",
                "Host": "mailer.pro.yapo.cl"}

    def send(self):
        body = {"to": self._to,
                "subject": self._subject,
                "html_message": self._message,
                "name": [self._name]}
        if self.to_attach:
            body["filename"] = self._filename
            body["binary_file"] = self._binary
            body["file_content_type"] = self._file_type
        
        r = requests.post("http://mailer.pro.yapo.cl/api/v1/postfix",
                          headers=self.headers(),
                          data=json.dumps(body))
        self.log.info("Email response: {}".format(r.text))
