import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

# GStreamer 초기화
Gst.init(None)

# 파이프라인 구성
pipeline = Gst.parse_launch("mfvideosrc ! queue ! videoconvert ! queue ! autovideosink")

# 파이프라인 실행
pipeline.set_state(Gst.State.PLAYING)

# 종료 시까지 대기
bus = pipeline.get_bus()
msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE, Gst.MessageType.ERROR | Gst.MessageType.EOS)

# 파이프라인 중지
pipeline.set_state(Gst.State.NULL)
