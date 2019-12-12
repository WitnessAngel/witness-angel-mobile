from waclient.common_config import IS_ANDROID, INTERNAL_CACHE_DIR
from wacryptolib.sensor import TarfileAggregator
from wacryptolib.utilities import TaskRunnerStateMachineBase

from kivy.logger import Logger as logger


class MicrophoneSensor(TaskRunnerStateMachineBase):

    _recorder = None  # Android MediaRecorder instance
    _output_file = None  # File in CACHE directory

    def __init__(self, tarfile_aggregator: TarfileAggregator):
        super().__init__()
        self._tarfile_aggregator = tarfile_aggregator

    def start(self):
        super().start()

        logger.info("Building microphone media recorder")

        #See https://stackoverflow.com/questions/13974234/android-record-mic-to-bytearray-without-saving-audio-file/42750515 to bypass disk
        temp_output_file = INTERNAL_CACHE_DIR.joinpath("temp_microphone_output_file.dat")
        self._output_file = temp_output_file

        if IS_ANDROID:

            from jnius import autoclass

            # Delayed creation, o avoid berakage at service launch
            MediaRecorder = autoclass('android.media.MediaRecorder')
            AudioSource = autoclass('android.media.MediaRecorder$AudioSource')
            OutputFormat = autoclass('android.media.MediaRecorder$OutputFormat')
            AudioEncoder = autoclass('android.media.MediaRecorder$AudioEncoder')

            # create out recorder
            recorder = MediaRecorder()
            self._recorder = recorder

            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(OutputFormat.MPEG_4)
            recorder.setAudioEncoder(AudioEncoder.AAC)  # Take OPUS Later (Added in API level 29)
            recorder.setAudioSamplingRate(16000)
            # mRecorder.setAudioEncodingBitRate(384000);

            recorder.setOutputFile(str(temp_output_file))
            recorder.prepare()

            recorder.start()

        logger.info("Starting microphone media recorder")


    def stop(self):
        super().stop()

        logger.info("Stopping microphone media recorder")

        if IS_ANDROID:
            recorder = self._recorder
            recorder.stop()
            recorder.release()

        temp_output_file = self._output_file
        logger.info("Microphone media recorder stopped, see file %s" % temp_output_file)
        self._output_file = None


        """
        self._tarfile_aggregator.add_record(
                sensor_name: str,
                from_datetime: datetime,
                to_datetime: datetime,
                extension: str,
                data: bytes,)
        """


def get_file_provider(tarfile_aggregator):
    return MicrophoneSensor(tarfile_aggregator=tarfile_aggregator)
