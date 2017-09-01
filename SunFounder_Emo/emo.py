class _Basic_class(object):
    import logging

    _class_name = '_Basic_class'
    _DEBUG = 'error'
    DEBUG_LEVELS = {'debug': logging.DEBUG,
              'info': logging.INFO,
              'warning': logging.WARNING,
              'error': logging.ERROR,
              'critical': logging.CRITICAL,
              }
    DEBUG_NAMES = ['critical', 'error', 'warning', 'info', 'debug']

    def __init__(self):v

    def logger_setup(self):
        self.logger = self.logging.getLogger(self._class_name)
        self.ch = self.logging.StreamHandler()
        form = "%(asctime)s [%(levelname)s] %(message)s"
        self.formatter = self.logging.Formatter(form)
        self.ch.setFormatter(self.formatter)
        self.logger.addHandler(self.ch)
        self._debug    = self.logger.debug
        self._info     = self.logger.info
        self._warning  = self.logger.warning
        self._error    = self.logger.error
        self._critical = self.logger.critical

    @property
    def DEBUG(self):
        return self._DEBUG

    @DEBUG.setter
    def DEBUG(self, debug):
        if debug in range(5):
            self._DEBUG = self.DEBUG_NAMES[debug]
        elif debug in self.DEBUG_NAMES:
            self._DEBUG = debug
        else:
            raise ValueError('Debug value must be 0(critical), 1(error), 2(warning), 3(info) or 4(debug), not \"{0}\".'.format(debug))  
        self.logger.setLevel(self.DEBUG_LEVELS[self._DEBUG])
        self.ch.setLevel(self.DEBUG_LEVELS[self._DEBUG])
        self._debug('Set logging level to [%s]' % self._DEBUG)

    def end(self):
        pass

class Emo(_Basic_class):
    import spidev
    import emo_maps

    OFF = [
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00,
        0x00, 0x00, 0x00]

    _class_name = 'Emo'

    def __init__(self, ce=0):
        self.ce = ce
        self.logger_setup()
        self.spi = self.spidev.SpiDev()
        self.spi.open(0,0)

        self.alphabet = self.emo_maps.Alphabet()
        self.emotions = self.emo_maps.Emotions()
        self.pictures = self.emo_maps.Pictures()

    def show_bytes(self, _bytes):
        if not self.get_start():
            return False
        self.spi.writebytes(0x02)  # If emo get 0x02, it begin to store the HEX data
        self.spi.writebytes(_bytes)
        return True

    def show_bits(self, _bits_list):
        _bytes = []
        if len(_bits_list) != 8:
            self._error("arguement should be list of 8 lines of strings")
        for _bits in _bits_list:
            _bits = _bits.replace(',', '').replace(' ', '')
            if len(_bits) != 24:
                self._error('every item in the list should be string with exact 24 "0" and "1" representing "off" and "on"')
            _byte0 = _bits[:8]
            _byte0 = int(_byte0, base=2)
            _bytes.append(_byte0)
            _byte1 = _bits[8:16]
            _byte1 = int(_byte1, base=2)
            _bytes.append(_byte1)
            _byte2 = _bits[16:]
            _byte2 = int(_byte2, base=2)
            _bytes.append(_byte2)
        self.show_bytes(_bytes)

    def string_to_map(self, s):
        smap = []
        for i in range(8):
            bits = ''
            for letter in s:
                try:
                    bits += self.alphabet.normal(letter)[-i-1]
                except:
                    for j in range(len(self.alphabet.normal(letter)[0])):
                        bits += '0'
                bits += '0'
            smap.append(bits)
        smap.reverse()
        #for i in smap:
        #    print i
        return smap

    def map_len(self, s):
        smap = self.string_to_map(s)
        return len(smap[0])

    def off(self):
        #send_bytes(self.OFF)
        self.show_bytes(self.OFF)

    def show_string(self, s, pos=0):
        bits_list = []
        smap = self.string_to_map(s)
        for i in range(8):
            temp = ''
            if pos <= 0:
                for j in range(-pos,24-pos):
                    try:
                        temp += smap[i][j]
                    except:
                        temp += '0'
            else:
            # add 0 at front
                for j in range(pos):
                    temp += '0'
                for j in range(24-pos):
                    try:
                        temp += smap[i][j]
                    except:
                        temp += '0'
            bits_list.append(temp)
        self.show_bits(bits_list)
        #for i in bits_list:
        #    print i
        return len(smap[0])

    def show_emo(self, emo):
        if emo in self.emotions._emotions.keys():
            self.show_bits(self.emotions.emotion(emo))

        if emo in self.pictures._pictures.keys():
            self.show_bits(self.pictures.picture(emo))

    def get_start(self):
        count = 0
        while True:
            a_status = self.spi.writebytes(0x01) # send start signel 0x01 and get respond
            if (a_status == 0x01): # If emo get 0x01, and get start, it respond 0x01
                break;
            count = count + 1
            if (count>23): # emo not get start, and over time
                return false
        return true

    @property
    def supported_character(self):
        self._supported_character = ''
        for key in self.alphabet._normal.keys():
            if key != 'ERROR_CHAR':
                self._supported_character += key
        return self._supported_character

    @property
    def supported_emotions(self):
        self._supported_emotions = ''
        for key in self.emotions._emotions.keys():
            self._supported_emotions += key
            self._supported_emotions += '  '
        return self._supported_emotions

    @property
    def supported_pictures(self):
        self._supported_pictures = ''
        for key in self.pictures._pictures.keys():
            self._supported_pictures += key
            self._supported_pictures += '  '
        return self._supported_pictures

    def print_supported(self):
        print ("supported character:\n  %s \n"%self.supported_character)
        print ("supported emotions:\n  %s \n"%self.supported_emotions)
        print ("supported pictures:\n  %s \n"%self.supported_pictures)


def supported():
    lm = Emo()
    lm.print_supported()

def test_character():
    lm = Emo()
    value = ';) :( :D'
    value_len = lm.map_len(value)
    for i in range(value_len):
        lm.show_string(value, -i+10)
        time.sleep(0.1)

def test_emotion():
    lm = Emo()
    for x in range(1,3):
        lm.show_emo("look1")
        time.sleep(0.3)

        lm.show_emo("look2")
        time.sleep(0.3)

        lm.show_emo("look3")
        time.sleep(0.3)

        lm.show_emo("look4")
        time.sleep(0.3)

        lm.show_emo("look1")
        time.sleep(0.3)

def test_animate():
    lm = Emo()
    lm.show_emo("pac_man1")
    time.sleep(0.8)

    lm.show_emo("pac_man2")
    time.sleep(0.8)

    lm.show_emo("pac_man3")
    time.sleep(0.8)


if __name__ == '__main__':
    import time
    try:
        supported()
        while True:
            test_character()
            time.sleep(0.5)
            test_animate()
            time.sleep(0.5)
            test_emotion()
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass

