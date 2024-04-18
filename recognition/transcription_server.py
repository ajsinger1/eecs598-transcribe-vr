from typing import Tuple
import socketserver
import threading
from time import sleep
import logging

from deep_translator import GoogleTranslator

class TranscriptionServer(socketserver.TCPServer):
    class TranscriptionHandler(socketserver.StreamRequestHandler):
        def handle(self) -> None:
            # translator = GoogleTranslator(source='auto', target='en')
            if logging.getLogger().isEnabledFor(logging.DEBUG):
                print(f"Connected to {self.client_address}")
            while True:
                new_phrase = False
                recv = self.request.recv(2).decode()
                recv = recv[1]
                if recv == 'P':
                    new_phrase = True
                    recv = self.request.recv(3).decode()
                    recv = recv[-1]
                size = ""
                while recv != '>':
                    size += recv
                    recv = self.request.recv(1).decode()
                
                size = int(size)
                phrase = self.request.recv(size).decode()

                while len(phrase) < size:
                    phrase += self.request.recv(size - len(phrase)).decode()
                
                self.server.is_new_phrase = new_phrase

                # translate
                # translated = translator.translate(phrase)

                self.server.phrase = phrase
                sleep(0.1)

    def __init__(self, host: str, port: int) -> None:
        super().__init__((host, port), self.TranscriptionHandler)
        self.is_new_phrase = False
        self.phrase = ""
        self.thread = threading.Thread(target=self.serve_forever, daemon=True).start()
    
    def get_phrase(self) -> Tuple[bool,str]:
        is_new_phrase = self.is_new_phrase
        self.is_new_phrase = False
        return is_new_phrase, self.phrase
    
    
