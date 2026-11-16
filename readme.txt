多国人工智能评测基准互认验证台

运行验收：
python3 -m benchmark_federation run --fixture fixtures/acceptance.json --database /tmp/benchmark_federation.sqlite3 --output /tmp/benchmark_federation-output

核验：
python3 -m benchmark_federation verify --database /tmp/benchmark_federation.sqlite3 --output /tmp/benchmark_federation-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.recognition_signal.test_recognition_confidence -v

构建检查：
python3 -m compileall -q benchmark_federation tests
