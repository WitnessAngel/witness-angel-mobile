import threading
from datetime import timezone, datetime

from kivy.logger import Logger as logger

from waclient.common_config import IS_ANDROID, INTERNAL_CACHE_DIR
from wacryptolib.sensor import TarfileRecordAggregator
from wacryptolib.utilities import PeriodicTaskHandler, synchronized


class MicrophoneSensor(PeriodicTaskHandler):

    _recorder = None  # Android MediaRecorder instance

    _lock = threading.Lock()
    _current_start_time = None

    def __init__(self, interval_s: float, tarfile_aggregator: TarfileRecordAggregator):
        super().__init__(interval_s=interval_s, runonstart=False)
        self._tarfile_aggregator = tarfile_aggregator

    @property
    def temp_file_path(self):
        return INTERNAL_CACHE_DIR.joinpath("temp_microphone_output_file.dat")

    @property
    def temp_file_path_finished(self):
        return INTERNAL_CACHE_DIR.joinpath("temp_microphone_output_file.finished.dat")

    def _cleanup_temp_files(self):
        for filepath in (self.temp_file_path, self.temp_file_path_finished):
            try:
                filepath.unlink()  # TODO use missing_ok=True later
            except FileNotFoundError:
                pass

    def _do_start_recording(self):

        if IS_ANDROID:

            # See https://stackoverflow.com/questions/13974234/android-record-mic-to-bytearray-without-saving-audio-file/42750515 to bypass disk

            from jnius import autoclass

            # Delayed creation, o avoid berakage at service launch
            MediaRecorder = autoclass("android.media.MediaRecorder")
            AudioSource = autoclass("android.media.MediaRecorder$AudioSource")
            OutputFormat = autoclass("android.media.MediaRecorder$OutputFormat")
            AudioEncoder = autoclass("android.media.MediaRecorder$AudioEncoder")

            # create out recorder
            recorder = MediaRecorder()
            self._recorder = recorder

            recorder.setAudioSource(AudioSource.MIC)
            recorder.setOutputFormat(OutputFormat.MPEG_4)
            recorder.setAudioEncoder(
                AudioEncoder.AAC
            )  # Take OPUS Later (Added in API level 29)
            recorder.setAudioSamplingRate(16000)
            # mRecorder.setAudioEncodingBitRate(384000);

            recorder.setOutputFile(str(self.temp_file_path))
            recorder.prepare()
            recorder.start()

        else:
            pass  # Do nothing for now, on PC and such

        self._current_start_time = datetime.now(
            tz=timezone.utc  # TODO make datetime utility with TZ
        )

    def _do_stop_recording(self):

        if IS_ANDROID:
            recorder = self._recorder
            recorder.stop()
            recorder.release()
            self._recorder = None
        else:
            # We fake the output of audio data by the media recorder
            self.temp_file_path.write_bytes(b"fake_microphone_recording_data")

        temp_file_path = self.temp_file_path
        if temp_file_path.exists():
            if (
                self.temp_file_path_finished.exists()
            ):  # Should have been deleted by data pusher
                logger.warning(
                    "Beware, microphone recorder unexpectedly overwrites temporary file %s"
                    % self.temp_file_path_finished.name
                )
            temp_file_path.rename(self.temp_file_path_finished)
        else:
            logger.warning(
                "Temporary microphone file %r is missing" % temp_file_path.name
            )

        self._current_start_time = None

    def _do_push_temporary_file_to_aggregator(self, from_datetime, to_datetime):
        assert from_datetime and to_datetime, (from_datetime, to_datetime)
        if not self.temp_file_path_finished.exists():
            return  # Might be a user's manual action?
        payload = self.temp_file_path_finished.read_bytes()
        self.temp_file_path_finished.unlink()  # Immediate safety
        self._tarfile_aggregator.add_record(
            sensor_name="microphone",
            from_datetime=from_datetime,
            to_datetime=to_datetime,
            extension=".mp4",  # Beware, change this if recorder output format changes!
            payload=payload,
        )

    @synchronized
    def _offloaded_run_task(self):
        """
        Full override of TaskRunnerStateMachineBase method, which just restarts the recording
        while switching output files.
        """
        if not self.is_running:
            return  # Thread looped one last time after sensor got stopped, forget about it

        logger.info("Changing the output file of microphone recorder")
        from_datetime = self._current_start_time
        to_datetime = datetime.now(
            tz=timezone.utc  # TODO make datetime utility with TZ
        )

        self._do_stop_recording()  # Renames target file
        self._do_start_recording()  # Must be restarted immediately, to avoid missing audio data

        self._do_push_temporary_file_to_aggregator(
            from_datetime=from_datetime, to_datetime=to_datetime
        )

    @synchronized
    def start(self):
        super().start()

        logger.info("Starting microphone media recorder")
        self._cleanup_temp_files()  # Security
        self._do_start_recording()
        logger.info("Started microphone media recorder")

    @synchronized
    def stop(self):
        super().stop()

        logger.info("Stopping microphone media recorder")
        from_datetime = self._current_start_time
        to_datetime = datetime.now(
            tz=timezone.utc  # TODO make datetime utility with TZ
        )
        self._do_stop_recording()
        self._do_push_temporary_file_to_aggregator(
            from_datetime=from_datetime, to_datetime=to_datetime
        )
        self._cleanup_temp_files()  # Double security
        logger.info("Stopped microphone media recorder")


def get_microphone_sensor(interval_s, tarfile_aggregator):
    return MicrophoneSensor(
        interval_s=interval_s, tarfile_aggregator=tarfile_aggregator
    )
