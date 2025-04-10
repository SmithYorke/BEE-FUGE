from music21 import converter, note, stream, tempo, midi
import random
import matplotlib.pyplot as plt

# ========== 控制器 控制与配置参数 ==========
CONTROL = {

    "population_size": 50000,  # 每轮生成的旋律个体数
    "elite_percent": 0.1,     # 精英个体比例
    "iterations": 20,          # 每轮迭代次数
    "midi_path": r"D:\\byzBach\\check7.mid",  # 初始主题文件路径
    "theme_reuse_ratio": 0.95,  # 普通小节中复现主题节奏或音高的概率
    "theme_reuse_interval": 3,  # 每隔几小节强制复现一次主题
    "theme_reuse_length": 4,    # 复现片段的长度（单位：音符数）
    "theme_octave_choices": [-12, 0, 12],  # 复现时允许的八度位移
    "theme_octave_shift_prob": 0.1,        # 复现时进行八度变换的概率
    "force_theme_recurrence": True,        # 是否启用强制复现机制
    "cost_weights": {
        "out_of_key": 12,              # 非调内音的惩罚
        "length_diff": 9,              # 音符数量与主题不同的惩罚
        "interval_penalty": 9,         # 音程波动与主题不一致的惩罚
        "repeat_penalty": 7,           # 连续重复音的惩罚
        "fluctuation_penalty": 12,     # 音高不活跃的惩罚
        "triple_repeat": 5,            # 三连音完全重复的惩罚
        "theme_match_bonus": -20,      # 与主题段落完全匹配的奖励（负数即为加分）
        "richness_bonus": -8,          # 含复杂节奏结构的奖励
        "min_note_count": 6,           # 每小节至少音符数量
        "note_count_penalty": 5,       # 若不够音符数时的每个单位惩罚
        "has_arpeggio_bonus": -4,      # 包含琶音结构的奖励
        "has_syncopation_bonus": -9,    # 包含切分节奏的奖励
        "note_count_penalty" : 5
    }
}


TIME_SIGNATURE = (4, 4)
BEATS_PER_MEASURE = TIME_SIGNATURE[0]
TOTAL_QUARTER_BEATS = 4.0
DURATION_OPTIONS = [0.25, 0.5, 1.0, 2.0]
ARPEGGIO_PROB = 0.4

PITCH_RANGE = [f"{n}{o}" for o in range(2, 7) for n in ["C", "D", "E", "F", "G", "A", "B"]]
OUT_OF_KEY = [f"{n}#{o}" for o in range(2, 7) for n in ["C", "D", "F", "G", "A"]]
OUT_OF_KEY_PROB = 0.05

CHORD_PROGRESSIONS = [
    ["C4", "E4", "G4", "B4"], ["D4", "F4", "A4", "C5"], ["E4", "G4", "B4", "D5"],
    ["F4", "A4", "C5", "E5"], ["G4", "B4", "D5", "F5"], ["A4", "C5", "E5", "G5"],
    ["D4", "F#4", "A4", "C5"], ["G4", "B4", "D5", "F#5"], ["C4", "E4", "G4", "C5"],
    ["E3", "G4", "C5", "A4"], ["F#4", "A4", "C#5", "E5"],
    ["Bb3", "D4", "F4"], ["Ab3", "C4", "Eb4"], ["B3", "D#4", "F#4"]
]

def get_current_chord(measure_index):
    idx = ((measure_index - 1) // 4) % len(CHORD_PROGRESSIONS)
    return CHORD_PROGRESSIONS[idx]
def set_tempo(score, bpm=100):
    mm = tempo.MetronomeMark(number=bpm)
    score.insert(0, mm)
    return score

TIME_SIGNATURE = (4, 4)
BEATS_PER_MEASURE = TIME_SIGNATURE[0]
PITCH_RANGE = [
    "C2","D2","E2","F2","G2","A2","B2",
    "C3","D3","E3","F3","G3","A3","B3",
    "C4","D4","E4","F4","G4","A4","B4",
    "C5","D5","E5","F5","G5","A5","B5",
    "C6","D6","E6","F6","G6"
]
OUT_OF_KEY = [
    "C#2","D#2","F#2","G#2","A#2",
    "C#3","D#3","F#3","G#3","A#3",
    "C#4","D#4","F#4","G#4","A#4",
    "C#5","D#5","F#5","G#5","A#5",
    "C#6","D#6","F#6","G#6","A#6"
]
OUT_OF_KEY_PROB = 0
DURATION_OPTIONS = [4.0,2.0,1.0,0.5]
ARPEGGIO_PROB = 0.9
TOTAL_QUARTER_BEATS = 4.0






# ========= 二基础功能函数（低耦合） =========

def transpose_pitch(pitch, semitones):

    """
    对给定音高进行转调，输入音高名称和转调半音数，返回转调后的音高名称。
    """
    mapping = {
        "C4": 60, "C#4": 61, "D4": 62, "D#4": 63, "E4": 64, "F4": 65,
        "F#4": 66, "G4": 67, "G#4": 68, "A4": 69, "A#4": 70, "B4": 71,
        "C5": 72, "C#5": 73, "D5": 74, "D#5": 75, "E5": 76, "F5": 77,
        "F#5": 78, "G5": 79, "G#5": 80, "A5": 81, "A#5": 82, "B5": 83,
    }
    reverse_mapping = {v: k for k, v in mapping.items()}
    midi_val = mapping.get(pitch, 60) + semitones
    # 防止转调后超出范围（例如超出音域范围则自动纠正）
    midi_val = min(max(midi_val, 60), 83)  # 限制在C4-B5之间
    return reverse_mapping.get(midi_val, "C4")

def is_harmonious_chord(answer, counter):
        pitches = set(p for p, _ in answer + counter)
        return any(chord.issubset(pitches) for chord in baroque_chords)

def set_tempo(score, bpm=100):
    mm = tempo.MetronomeMark(number=bpm)
    score.insert(0, mm)
    return score

def analyze_single_notes(midi_path):
    s = converter.parse(midi_path).flatten().notes
    results = []
    for e in s:
        if isinstance(e, note.Note):
            results.append({"pitch": e.pitch.nameWithOctave,
                            "offset": e.offset,
                            "duration": e.duration.quarterLength})
    return results

def extract_theme(notes_info):
    return [(n["pitch"], n["duration"]) for n in notes_info]



    recurrence_interval = CONTROL["theme_reuse_interval"]

    # 检查是否到达强制复现的间隔
    if CONTROL["force_theme_recurrence"] and measure_index % recurrence_interval == 0:
        print(f"🔁 强制复现主题，第{measure_index}小节")
        
        # 确定是否进行八度变化
        if random.random() < CONTROL["theme_octave_shift_prob"]:
            octave_shift = random.choice([-12, 12])
        else:
            octave_shift = 0

        # 完整复现主题（节奏和音高完全一致，可能八度变动）
        reused_theme = [(transpose_pitch(p, octave_shift), d) for p, d in theme]
        return reused_theme

    # 如果不是复现小节，执行普通旋律生成
    current_chord = get_current_chord(measure_index)
    theme_rhythm = [d for _, d in theme]
    melody = global_search_with_chord(current_chord, theme_rhythm)

    return melody


# ========= 三、旋律生成模块 =========


def global_search_with_richness():
    melody, used_beats = [], 0
    syncopation_used = False
    while used_beats < BEATS_PER_MEASURE:
        if random.random() < ARPEGGIO_PROB and used_beats + 1.5 <= BEATS_PER_MEASURE:
            for pitch, dur in generate_arpeggio_segment():
                if used_beats + dur > BEATS_PER_MEASURE:
                    break
                melody.append((pitch, dur))
                used_beats += dur
            continue

        pitch = random.choice(OUT_OF_KEY if random.random() < OUT_OF_KEY_PROB else PITCH_RANGE)

        if not syncopation_used and used_beats in [0, 1, 2] and random.random() < 0.5:
            for dur in random.choice([
                [0.75, 0.25, 1.0, 2.0],
                [1.5, 0.5, 1.0],
                [0.5, 1.5, 0.5, 1.5],
                [0.25]*4 + [1.0, 2.0]
            ]):
                if used_beats + dur > BEATS_PER_MEASURE:
                    break
                melody.append((pitch, dur))
                used_beats += dur
            syncopation_used = True
        else:
            dur = min(random.choice(DURATION_OPTIONS), BEATS_PER_MEASURE - used_beats)
            melody.append((pitch, dur))
            used_beats += dur
    return melody

def global_search_with_chord(chord, rhythm=None):
    melody, used_beats, i = [], 0, 0
    while used_beats < TOTAL_QUARTER_BEATS:
        pitch = random.choice(chord)
        dur = rhythm[i] if rhythm and i < len(rhythm) else random.choice(DURATION_OPTIONS)
        dur = min(dur, TOTAL_QUARTER_BEATS - used_beats)
        melody.append((pitch, dur))
        used_beats += dur
        i += 1
    return melody

def generate_arpeggio_segment():
    progressions = CHORD_PROGRESSIONS
    dur_pattern = random.choice([[0.5]*4, [0.25]*3 + [1.25], [0.75, 0.25, 0.5, 0.5]])
    selected = random.choice(progressions)
    return list(zip(selected[:len(dur_pattern)], dur_pattern))

def generate_third_voice_from_chord_root(measure_index):
    current_chord = get_current_chord(measure_index)
    roots = [note for note in current_chord if note.endswith("4") or note.endswith("3")]
    bass_candidates = [r.replace("4", "3") for r in roots]
    if not bass_candidates:
        bass_candidates = ["C3"]
    result = []
    used_beats = 0.0
    last_pitch = None
    while used_beats < BEATS_PER_MEASURE:
        dur = random.choice([2.0, 1.0])
        if used_beats + dur > BEATS_PER_MEASURE:
            dur = BEATS_PER_MEASURE - used_beats
        pitch = random.choice(bass_candidates)
        if pitch == last_pitch and random.random() < 0.5:
            continue
        result.append((pitch, dur))
        last_pitch = pitch
        used_beats += dur
    return result

def generate_third_voice(theme):
    third_voice = []
    available_durations = [1.0, 2.0, 0.5]
    used_beats = 0.0
    theme_pitches = [pitch for pitch, _ in theme]













# ========== 四、核心逻辑模块（结构） ==========

def generate_answer(theme, measure_index):

    recurrence_interval = CONTROL["theme_reuse_interval"]

    # 检查是否到达强制复现的间隔
    if CONTROL["force_theme_recurrence"] and measure_index % recurrence_interval == 0:
        print(f"🔁 强制复现主题，第{measure_index}小节")
        
        # 确定是否进行八度变化
        if random.random() < CONTROL["theme_octave_shift_prob"]:
            octave_shift = random.choice([-12, 12])
        else:
            octave_shift = 0

        # 完整复现主题（节奏和音高完全一致，可能八度变动）
        reused_theme = [(transpose_pitch(p, octave_shift), d) for p, d in theme]
        return reused_theme

    # 如果不是复现小节，执行普通旋律生成
    current_chord = get_current_chord(measure_index)
    theme_rhythm = [d for _, d in theme]
    melody = global_search_with_chord(current_chord, theme_rhythm)

    return melody

def generate_counter(theme, measure_index):
    best = None
    best_cost = float('inf')
    print(f"⏳ 正在生成第 {measure_index} 小节的 counter...")

    for i in range(CONTROL["iterations"]):
        print(f"  ➤ 迭代 {i+1}/{CONTROL['iterations']}")
        pop = [global_search_with_chord(get_current_chord(measure_index), None) for _ in range(min(CONTROL["population_size"], 500))]
        for melody in pop:
            c = cost(melody, theme)
            if c < best_cost:
                best = melody
                best_cost = c

    print(f"✅ 最佳counter cost={best_cost}，旋律为：{best}")
    return best

def generate_counter_subject(theme, answer):
    """
    基于主题旋律生成答题旋律，简单实现为主题下行五度转调。
    """
    transposition_interval = -5  # 下行五度（7个半音）
    return [(transpose_pitch(p, transposition_interval), d) for p, d in theme]

def generate_recursive_structure(start_theme, num_cycles=4):
    measures = []
    current_theme = start_theme[:]
    for i in range(num_cycles):
        print(f"\n🔁 第{i+1}轮: 生成答题和新对题")
        counter = generate_counter(current_theme, i*2 + 2)
        new_answer = generate_answer(counter, i*2 + 3)
        measures.append((current_theme, counter))
        measures.append((counter, new_answer))
        current_theme = new_answer
    return measures




# ========== 五、优化 ==========
def cost(melody, theme):
    weights = CONTROL["cost_weights"]
    def pitch_to_int(p):
        base = {n: i for i, n in enumerate(PITCH_RANGE + OUT_OF_KEY)}
        return base.get(p, 60)
    
    out_of_key_count = sum(p not in PITCH_RANGE for p, _ in melody)
    len_diff = abs(len(melody) - len(theme))
    overlap = min(len(melody), len(theme))
    intervals_m = [abs(pitch_to_int(melody[i+1][0]) - pitch_to_int(melody[i][0])) for i in range(overlap-1)]
    intervals_t = [abs(pitch_to_int(theme[i+1][0]) - pitch_to_int(theme[i][0])) for i in range(overlap-1)]
    avg_diff = sum(abs(i - t) for i, t in zip(intervals_m, intervals_t)) / (overlap-1) if overlap > 1 else 0

    penalty_interval = (max(0, 1 - avg_diff) + max(0, avg_diff - 3)) * weights["interval_penalty"]
    repeat_penalty = sum(1 for i in range(1, len(melody)) if melody[i][0] == melody[i-1][0]) * weights["repeat_penalty"]
    fluctuation_penalty = sum(1 for i in range(1, len(melody)-1) if abs(pitch_to_int(melody[i+1][0]) - pitch_to_int(melody[i][0])) - abs(pitch_to_int(melody[i][0]) - pitch_to_int(melody[i-1][0])) < 2) * weights["fluctuation_penalty"]
    triple_repeat = sum(1 for i in range(2, len(melody)) if melody[i][0] == melody[i-1][0] == melody[i-2][0]) * weights["triple_repeat"]
    # 音符数量惩罚项
    note_count_penalty = 0
    min_notes = weights.get("min_note_count", 6)
    if len(melody) < min_notes:
        note_count_penalty = (min_notes - len(melody)) * weights.get("note_count_penalty", 5)

    # 主题复现奖励（若连续6音节等于主题片段）
    theme_seq = [p for p, _ in theme]
    melody_seq = [p for p, _ in melody]
    match_bonus = 0
    for i in range(len(melody_seq) - 5):
        if melody_seq[i:i+6] == theme_seq[:6]:
            match_bonus += weights.get("theme_match_bonus", 0)

    return (
        out_of_key_count * weights["out_of_key"] +
        max(0, len_diff - 2) * weights["length_diff"] +
        penalty_interval +
        repeat_penalty +
        fluctuation_penalty +
        triple_repeat +
        match_bonus +
        note_count_penalty
)

    
COST_LOG = []

def counter_cost(counter_melody, previous_answer):
    richness = sum(1 for _, d in counter_melody if d in [0.25, 0.5])
    variation = sum(1 for i in range(1, len(counter_melody)) if counter_melody[i][0] != counter_melody[i-1][0])
    harmony = sum(1 for (p1, _), (p2, _) in zip(counter_melody, previous_answer) if p1 in get_current_chord(0) and p2 in get_current_chord(0))
    total_cost = -richness - variation + harmony
    COST_LOG.append(total_cost)
    return total_cost

def generate_population(n_candidates, theme, elite_percent=0.1):
    raw_population = []
    for idx in range(n_candidates):
        mel = global_search_with_richness()  # ← 更换为复杂旋律生成器
        c = cost(mel, theme)
        raw_population.append(Bee(mel, c, idx))
    raw_population.sort(key=lambda b: b.cost)

    elite_count = max(1, int(n_candidates * elite_percent))
    elites = raw_population[:elite_count]
    elites_sorted = sorted(elites, key=lambda b: smoothness(b.melody))

    baroque_chords = [
        {"C4", "E4", "G4"}, {"F4", "A4", "C5"}, {"G4", "B4", "D5"},
        {"A4", "C5", "E5"}, {"D4", "F4", "A4"}, {"E4", "G4", "B4"},
        {"C4", "E4", "A4"}, {"C4", "E4", "G4"}
    ]



    filtered_elites = []
    for i in range(0, len(elites_sorted)-1, 2):
        answer = elites_sorted[i].melody
        counter = elites_sorted[i+1].melody
        if is_harmonious_chord(answer, counter):
            filtered_elites.extend([elites_sorted[i], elites_sorted[i+1]])

    if not filtered_elites:
        print("⚠️ 未找到和谐配对的精英组合，退回基础精英")
        filtered_elites = elites_sorted

    print(f"\n 精英阶段筛选 (Top {elite_percent*100:.0f}% = {elite_count}个)：")
    for i, bee in enumerate(filtered_elites):
        print(f"  🎵 精英 {i+1}: Smoothness={smoothness(bee.melody)}, Cost={bee.cost}, Melody={bee.melody}")

    return filtered_elites

def elite_selection(population, elite_size=10):
    """
    从旋律种群中筛选Cost最低的前elite_size个旋律（精英蜂群）。
    默认保留10条最优旋律作为精英。
    返回精英蜂群列表（Bee对象）。
    """
    sorted_population = sorted(population, key=lambda bee: bee.cost)
    elite_bees = sorted_population[:elite_size]
    
    # 打印精英蜂旋律详细数据以便调试
    print(f"\n 已筛选出精英蜂旋律 (Cost前{elite_size}名)：")
    for idx, bee in enumerate(elite_bees, start=1):
        print(f"【 {idx}】 Cost: {bee.cost}, Melody: {bee.melody}")
    
    return elite_bees
# ========== 精英蜂群的旋律平滑度评分 ==========
def smoothness(melody):
    def pitch_to_int(p):
        mapping = {"C4":60,"D4":62,"E4":64,"F4":65,"G4":67,"A4":69,"B4":71,
                   "C5":72,"D5":74,"E5":76,"F5":77,"G5":79,"A5":81,"B5":83}
        return mapping.get(p,60)
    # 跳跃超过五度（7个半音）认为不平滑
    return sum(abs(pitch_to_int(melody[i+1][0])-pitch_to_int(melody[i][0])) > 5 for i in range(len(melody)-1))
















# 六、输出与可视化



def plot_cost_log():
    if COST_LOG:
        plt.figure(figsize=(8, 4))
        plt.plot(COST_LOG, marker='o', linestyle='-', color='blue')
        plt.title("Counter Cost Over Time")
        plt.xlabel("Generation Index")
        plt.ylabel("Cost Value")
        plt.grid(True)
        plt.tight_layout()
        plt.show()
   

def create_midi(theme, voices, filename):
    score = stream.Score()
    # 第一小节单独主题
    part_theme = stream.Part()
    for pitch, dur in theme:
        part_theme.append(note.Note(pitch, quarterLength=dur))
    score.append(part_theme)

    # 后续声部
    for voice in voices:
        part = stream.Part()
        for pitch, dur in voice:
            part.append(note.Note(pitch, quarterLength=dur))
        score.append(part)
    score.write('midi', fp=filename)

def create_fugue_with_structure(theme_notes, total_measures=12, bpm=116, filename=r"..."):
    score = stream.Score()
    set_tempo(score, bpm)

    # 插入主旋律
    append_theme_measure(score, theme_notes)

    # 初始化空声部
    parts = {name: stream.Part(id=name) for name in ["Answer_Part", "Counter_Part", "Bass_Part"]}
    for part in parts.values():
      m = stream.Measure(number=1)
      m.append(note.Rest(quarterLength=4.0))
      part.append(m)


    prev_theme = theme_notes

    for measure_index in range(2, total_measures + 1):
        print(f"\n🔸【生成第 {measure_index} 小节】")
        answer = generate_answer(prev_theme, measure_index)
        counter = generate_counter(prev_theme, measure_index)
        third = generate_third_voice_from_chord_root(measure_index) if measure_index >= 3 else [("C3", 4.0)]

        for part, notes in zip(parts.values(), [answer, counter, third]):
            m = stream.Measure(number=measure_index)
            for p, d in notes:
                m.append(note.Note(p, quarterLength=d))
            part.append(m)

        prev_theme = counter

    for part in parts.values():
        score.insert(0, part)

    score.write("midi", fp=filename)
    print(f"\n✅ 完成生成：{filename}")

def append_theme_measure(score, theme_notes):
    part_theme = stream.Part(id="Theme_Part")
    measure1 = stream.Measure(number=1)
    offset = 0.0
    for pitch, dur in theme_notes:
        n = note.Note(pitch, quarterLength=dur)
        n.offset = offset
        measure1.append(n)
        offset += dur
    part_theme.append(measure1)
    score.insert(0, part_theme)
    return part_theme


def analyze_single_notes(midi_path):
    s = converter.parse(midi_path).flatten().notes
    results = []
    for e in s:
        if isinstance(e, note.Note):
            results.append({"pitch": e.pitch.nameWithOctave,
                            "offset": e.offset,
                            "duration": e.duration.quarterLength})
    return results


def create_segmented_fugue(
    first_theme,
    total_measures=6,   # 指的是要生成多少轮对题+答题
    bpm=100,
    filename=r"D:\\byzBach\\final_fugue.mid"


):
    """
    逻辑：
      measure #1: 放 first_theme (单声部，仅4拍)
      measure #2: 第1次对题 (4拍)
      measure #3: 第1次答题 (4拍)
      measure #4: 第2次对题
      measure #5: 第2次答题
      ...
      这样每个对题、答题都在自己的单独小节，不会叠加。
    """

    # 1) 创建Score, 设置bpm
    score = stream.Score()
    set_tempo(score, bpm)

    fugue_part = stream.Part()
    fugue_part.id = "FuguePart"

    # ========== measure #1 ========== (仅主题)
    m1 = stream.Measure(number=1)
    offset_in_measure = 0.0
    for (pitch, dur) in first_theme:
        if offset_in_measure + dur > 4.0:
            break
        n = note.Note(pitch, quarterLength=dur)
        n.offset = offset_in_measure
        m1.append(n)
        offset_in_measure += dur
    fugue_part.append(m1)

    # 上一轮主题 = first_theme
    prev_theme = first_theme

    # ========== 从第1次对题+答题 到 第n次对题+答题 ==========
    # for i in range(1, total_measures+1):
    for i in range(1, total_measures + 1):
        # 对题小节 => measure(2 * i)
        measure_answer = stream.Measure(number=2*i)
        # 用上一小节主题生成对题
        pop = generate_population(5000, prev_theme)
        best_answer = pop[0].melody
        print(f"\n第{i}次 对题 = {best_answer}")

        offset_ans = 0.0
        for p, d in best_answer:
            if offset_ans + d > 4.0:
                break
            n = note.Note(p, quarterLength=d)
            n.offset = offset_ans
            measure_answer.append(n)
            offset_ans += d
        fugue_part.append(measure_answer)

        # 答题小节 => measure(2 * i + 1)
        measure_counter = stream.Measure(number=2*i + 1)
        best_counter = generate_counter_subject(prev_theme, best_answer)
        print(f"第{i}次 答题 = {best_counter}")

        offset_cnt = 0.0
        for p, d in best_counter:
            if offset_cnt + d > 4.0:
                break
            n = note.Note(p, quarterLength=d)
            n.offset = offset_cnt
            measure_counter.append(n)
            offset_cnt += d
        fugue_part.append(measure_counter)

        # 更新下一轮主题
        prev_theme = best_counter

    score.insert(0, fugue_part)
    score.write("midi", fp=filename)
    print(f"\n✅ 完成后输出 {2*total_measures+1} 个 measure (含主题)，保存到: {filename}")



def transpose_pitch(pitch, semitones):
    mapping = {}
    midi = 36
    for octave in range(2, 7):
        for note in ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]:
            key = f"{note}{octave}"
            mapping[key] = midi
            midi += 1
    reverse = {v: k for k, v in mapping.items()}
    return reverse.get(min(max(mapping.get(pitch, 60) + semitones, 36), 91), "C4")



# 随机生成带切分音的旋律
def global_search_with_syncopation():
    melody, used_beats = [], 0
    syncopation_used = False
    while used_beats < TOTAL_QUARTER_BEATS:
        pitch = random.choice(OUT_OF_KEY if random.random() < OUT_OF_KEY_PROB else PITCH_RANGE)
        
        # 引入切分可能性
        if not syncopation_used and used_beats in [0, 2] and random.random() < 0.3:
            dur_seq = [(1.5, 0.5), (0.75, 0.25)]
            chosen_seq = random.choice(dur_seq)
            for dur in chosen_seq:
                if used_beats + dur > TOTAL_QUARTER_BEATS:
                    dur = TOTAL_QUARTER_BEATS - used_beats
                melody.append((pitch, dur))
                used_beats += dur
            syncopation_used = True
        else:
            dur = random.choice(DURATION_OPTIONS)
            dur = min(dur, TOTAL_QUARTER_BEATS - used_beats)
            melody.append((pitch, dur))
            used_beats += dur
    return melody

# ========== 随机生成旋律 ==========
def global_search(debug=False):
    melody, used_beats = [], 0
    while used_beats < TOTAL_QUARTER_BEATS:
        pitch = random.choice(OUT_OF_KEY if random.random() < OUT_OF_KEY_PROB else PITCH_RANGE)
        dur = random.choice(DURATION_OPTIONS)
        dur = min(dur, TOTAL_QUARTER_BEATS - used_beats)  # 防止超拍
        melody.append((pitch, dur))
        used_beats += dur
    return melody





# ========== Bee类 ==========
class Bee:
    def __init__(self, melody, cost_val, counter):
        self.melody = melody
        self.cost = cost_val
        self.counter = counter
    def __repr__(self):
        return f"Bee(cost={self.cost}, melody={self.melody})"






# 精英蜂的二次优化
def elite_search(elite_bees):
    elite_ranked = sorted(elite_bees, key=lambda bee: smoothness(bee.melody))
    return elite_ranked[:20]  # 保留前20个最平滑旋律作为精英结果


# 和声协调检测（非常基础版）
def chord_harmony(melody1, melody2):
    harmonious_intervals = {0,3,4,5,7,8,9,12}  # 常见和谐音程（0度、3度、4度、5度等）
    def pitch_to_int(p): 
        mapping = {"C4":60,"C#4":61,"D4":62,"D#4":63,"E4":64,"F4":65,"F#4":66,
                   "G4":67,"G#4":68,"A4":69,"A#4":70,"B4":71,"C5":72,"C#5":73,"D5":74}
        return mapping.get(p,60)
    min_len = min(len(melody1), len(melody2))
    penalty = sum(abs(pitch_to_int(melody1[i][0])-pitch_to_int(melody2[i][0]))%30 not in harmonious_intervals for i in range(min_len))
    return penalty



# 检查两个音符是否和谐（和谐音程）
def is_harmonious(pitch1, pitch2):
    harmonious_intervals = {0, 3, 4, 5, 7, 8, 9, 12}
    def pitch_to_int(p):
        mapping = {"C4":60,"C#4":61,"D4":62,"D#4":63,"E4":64,"F4":65,"F#4":66,
                   "G4":67,"G#4":68,"A4":69,"A#4":70,"B4":71,"C5":72,"C#5":73,"D5":74,
                   "D#5":75,"E5":76,"F5":77,"F#5":78,"G5":79,"G#5":80,"A5":81,"A#5":82,"B5":83}
        return mapping[p]
    interval = abs(pitch_to_int(pitch1) - pitch_to_int(pitch2)) % 24
    return interval in harmonious_intervals



# 生成第三声部（仅2个和谐音）
def generate_third_voice(theme):
    third_voice = []
    available_durations = [1.0, 2.0, 0.5]  # 较长时值，避免复杂
    used_beats = 0.0
    theme_pitches = [pitch for pitch, _ in theme]

    # 尝试在主题中找到两个音与之形成和谐
    for pitch in theme_pitches:
        for candidate_pitch in PITCH_RANGE:
            if is_harmonious(pitch, candidate_pitch):
                duration = random.choice(available_durations)
                if used_beats + duration <= BEATS_PER_MEASURE:
                    third_voice.append((candidate_pitch, duration))
                    used_beats += duration
                    if len(third_voice) == 4 or used_beats >= BEATS_PER_MEASURE:
                        return third_voice
    return third_voice  # 返回不超过2个音的和谐旋律













def create_complete_fugue(theme_notes, total_measures=6, bpm=100, filename=r"D:\\byzBach\\full_fugue.mid"):
    """
    主程序: 
      - 第1小节: 只有主题
      - 第2小节: 新增对题
      - 第3小节起: 保持三声部(主题/对题/答题), 并使用 measure 对象顺序拼接
    """
    # 1. 建立总乐谱 Score，设置BPM
    full_score = stream.Score()
    set_tempo(full_score, bpm)
    
    # ========== 小节1: 仅主题单声部 ==========
    measure1 = stream.Measure(number=1)
    for pitch, dur in theme_notes:
        n = note.Note(pitch, quarterLength=dur)
        measure1.append(n)
    # 添加到一个 Part（主旋律）
    part_theme = stream.Part()
    part_theme.id = "Part_Theme"
    part_theme.append(measure1)
    
    full_score.append(part_theme)

    previous_theme = theme_notes
    previous_answer = None
    previous_counter = None

    # ========== 从第2小节开始，逐小节生成 ==========
    for measure_index in range(2, total_measures + 1):
        print(f"\n🔸【生成第 {measure_index} 小节】")

        # 生成对题(新主题)
        population = generate_population(5000, previous_theme)
        best_bee = elite_selection(population)[0]   # cost最低
        best_answer = best_bee.melody
        print(" - 对题:", best_answer)

        # 生成答题(转调)
        best_counter = generate_counter_subject(previous_theme, best_answer)
        print(" - 答题:", best_counter)

        # 每小节都有 measure 对象
        measure2 = stream.Measure(number=measure_index)  # 对题
        for pitch, dur in best_answer:
            n = note.Note(pitch, quarterLength=dur)
            measure2.append(n)

        # 声部2: 同一个 part？
        # 为了不重叠，这里也可以放在另一个 part 里
        measure3 = stream.Measure(number=measure_index)  # 答题
        for pitch, dur in best_counter:
            n = note.Note(pitch, quarterLength=dur)
            measure3.append(n)

        # 第三小节之后可以加一个第三声部, 这里仅示例
        # 如果 measure_index >= 3:
        #   measure4 = stream.Measure(number=measure_index)
        #   # 自行生成第三声部旋律
        #   measure4.append(...)
        #   # 添加到 part3
        #   ...

        # 继续将 measure2, measure3 添加到新的 Part
        part_answer = stream.Part()
        part_answer.id = f"Part_Answer_{measure_index}"
        part_answer.append(measure2)
        
        part_counter = stream.Part()
        part_counter.id = f"Part_Counter_{measure_index}"
        part_counter.append(measure3)

        # 插入到 Score
        full_score.append(part_answer)
        full_score.append(part_counter)

        # 更新 供下一轮使用
        previous_theme = best_answer
        previous_answer = best_answer
        previous_counter = best_counter

    # 4. 写出MIDI
    full_score.write('midi', fp=filename)
    print(f"\n✅ 已生成共 {total_measures} 小节的赋格： {filename}")




def global_search_single_measure():
    melody, used_beats = [], 0
    while used_beats < BEATS_PER_MEASURE:
        pitch = random.choice(OUT_OF_KEY if random.random() < OUT_OF_KEY_PROB else PITCH_RANGE)
        dur = random.choice(DURATION_OPTIONS)
        dur = min(dur, BEATS_PER_MEASURE - used_beats)
        melody.append((pitch, dur))
        used_beats += dur
    return melody



# 提取旋律主题
def extract_theme(notes_info):
    return [(n["pitch"], n["duration"]) for n in notes_info]

# 设置乐谱的节奏
def set_tempo(score, bpm=100):
    mm = tempo.MetronomeMark(number=bpm)
    score.insert(0, mm)
    return score


STYLE_PRESETS = {
    1: "Baroque",
    2: "Modern Jazz",
    3: "Contemporary Pop",
    4: "Experimental Atonal"
}

def apply_style(style_id):
    style = STYLE_PRESETS.get(style_id, "Baroque")
    print(f"🎼 已选择风格: {style}")
    cw = CONTROL["cost_weights"]
    
    if style_id == 1:
        cw.update({"interval_penalty": 10, "repeat_penalty": 4, "fluctuation_penalty": 10,
                   "theme_match_bonus": -20, "has_arpeggio_bonus": -4})
    elif style_id == 2:
        cw.update({"interval_penalty": 3, "out_of_key": 2, "fluctuation_penalty": 3,
                   "has_syncopation_bonus": -8, "repeat_penalty": 10})
    elif style_id == 3:
        cw.update({"repeat_penalty": 2, "theme_match_bonus": -30, "triple_repeat": 0,
                   "length_diff": 5, "interval_penalty": 5})
    elif style_id == 4:
        cw.update({"out_of_key": 0, "interval_penalty": 1, "fluctuation_penalty": 1,
                   "repeat_penalty": 12, "theme_match_bonus": 0})


if __name__ == "__main__":
    print("🎧 请选择音乐风格：\n1：巴洛克\n2：现代爵士\n3：当代流行\n4：实验无调性")
    choice = int(input("请输入风格编号（1~4）："))
    apply_style(choice)

    midi_file_path = CONTROL.get("midi_path", r"D:\\byzBach\\check1.mid")
    s = converter.parse(midi_file_path).flatten().notes
    theme_notes = [(n.pitch.nameWithOctave, n.duration.quarterLength) for n in s if isinstance(n, note.Note)]

    create_fugue_with_structure(
        theme_notes=theme_notes,
        total_measures=32,
        bpm=117,
        filename=r"D:\\byzBach\\structured_fugue.mid"
    )
