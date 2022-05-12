"""
Data container for meme results.

"""
from dataclasses import dataclass
from typing import Optional

from project import models as m

@dataclass
class Result:

    meme: Optional[m.Meme] = None
    is_db_ready: bool = False

    def __init__(self, url: str) -> None:
        self.meme = m.Meme(url=url)

    def set_meme_context(self, ctx: m.MemeContext):
        self.meme.context = ctx
    
    def set_meme_context_from_args(self, origin: str, post_url: str):
        self.meme.context = m.MemeContext(origin=origin, post_url=post_url)
    
    def set_meme_image(self, mimg: m.MemeImage):
        self.meme.image = mimg
    
    def set_meme_image_from_args(self, width: int = None, height: int = None, channels: int = None, format: int = None):
        self.meme.image = m.MemeImage(width=width, height=height, channels=channels, format=format)

    def add_meme_text(self, mtext: m.MemeText):
        self.meme.texts.append(mtext)
    
    def add_meme_text_from_args(self, body: str, text_type: str, confidence: float):
        self.meme.texts.append(m.MemeText(body=body, text_type=text_type, confidence=confidence))
    
    def add_meme_sentence(self, mtext: m.MemeText, msentence: m.MemeSentence):
        mtext.sentences.append(msentence)

    def add_meme_sentence_from_args(self, mtext: m.MemeText, sentence: str):
        mtext.sentences.append(m.MemeSentence(sentence=sentence))

    def add_meme_chunk(self, msentence: m.MemeSentence, mchunk: m.MemeChunk):
        msentence.chunks.append(mchunk)

    def add_meme_chunk_from_args(self, msentence: m.MemeSentence, chunk: str, is_named_entity: bool):
        msentence.chunks.append(m.MemeChunk(chunk=chunk, is_named_entity=is_named_entity))
    
    def add_meme_word(self, msentence: m.MemeSentence, mword: m.MemeWord):
        msentence.words.append(mword)
    
    def add_meme_word_from_args(self, msentence: m.MemeSentence, word: str, pos_tag: str = None, lemma: str = None):
        msentence.words.append(m.MemeWord(word=word, pos_tag=pos_tag, lemma=lemma))

    def __repr__(self) -> str:
        return f"<Result {self.meme.url if len(self.meme.url) < 30 else self.meme.url[:28] + '...'}>"
