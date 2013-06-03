import logging

logger = logging.getLogger('bpm.logger')


class BPMLogger(object):

    def write(self, text):
        logger.info(text)

