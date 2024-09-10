from flask import Flask, request, jsonify, render_template
import re

app = Flask(__name__)

def srt_to_lrc(srt_content):
    lrc_lines = []
    srt_blocks = re.split(r'\n\s*\n', srt_content.strip())  # 分割不同字幕块

    for block in srt_blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            continue
        # 跳过第一个序号行
        time_line = lines[1]
        text_lines = lines[2:]

        # 提取时间
        match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
        if not match:
            return None
        start_time, _ = match.groups()
        lrc_timestamp = srt_time_to_lrc_time(start_time)

        # 将字幕文本与时间戳组合
        for text in text_lines:
            lrc_lines.append(f"{lrc_timestamp}{text}")

    return '\n'.join(lrc_lines)

def srt_time_to_lrc_time(srt_time):
    # 将 SRT 时间格式 hh:mm:ss,ms 转换为 LRC 时间格式 [mm:ss.xx]
    hours, minutes, seconds = srt_time.split(':')
    seconds, milliseconds = seconds.split(',')
    total_minutes = int(hours) * 60 + int(minutes)
    lrc_timestamp = f"[{total_minutes:02}:{int(seconds):02}.{int(milliseconds[:2]):02}]"
    return lrc_timestamp

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    srt_content = ''
    if 'srt_content' in request.form:
        srt_content = request.form['srt_content']
    elif 'srt_file' in request.files:
        srt_file = request.files['srt_file']
        srt_content = srt_file.read().decode('utf-8')

    if not srt_content:
        return jsonify({"error": "No SRT content provided"}), 400

    lrc_content = srt_to_lrc(srt_content)
    if lrc_content is None:
        return jsonify({"error": "Invalid SRT format"}), 400

    return jsonify({"lrc_content": lrc_content})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
