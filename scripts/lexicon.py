# -*- coding: utf-8 -*-
"""Rules for stop-shitting-in-my-text.

Each rule can be edited by hand. Fields:

    id             stable identifier used in reports
    severity       block | warn | hint
    langs          zh | en | any
    category       human-facing grouping
    pattern        Python re pattern; inline flags like (?i) are allowed
    why            one sentence: what the tell signals
    fix            one sentence: what to write instead
    min_count      do not report below this many hits (default 1)
    max_per_1000   do not report at or below this density; warn escalates
                   to block above 2.5x this value

Density matters more than raw counts: one "对齐" can be a layout term, five
in a memo is a smell. Rules without max_per_1000 always report at min_count.
"""


_POSITIVE_TRAIT = (
    r"(?<!不)好|(?<!不)快|(?<!不)稳|(?<!不)强|省|便宜|高效|简单|方便|可靠|"
    r"安全|清晰|灵活|完整|丰富|提升|改善|优势|增长|成功|喜欢|满意|值得|"
    r"领先|优秀|强大|轻松|顺畅|稳定|划算|耐用|效率(?:很|较|非常)?高|"
    r"收益(?:很|较|非常)?高|质量(?:很|较|非常)?高|"
    r"性价比(?:很|较|非常)?高|成本(?:很|较|非常)?低|价格(?:很|较|非常)?低"
)
_NEGATIVE_TRAIT = (
    r"慢|贵|难|复杂|风险|问题|缺陷|不足|下降|失败|糟糕|麻烦|限制|瓶颈|"
    r"脆弱|不稳定|不稳|不安全|不好|不快|不强|不好用|模糊|冗长|昂贵|难用|"
    r"费时|费力|出错|风险高|成本高|价格高|效率低|质量差|有挑战"
)


def _same_polarity(pos, neg):
    """Two clauses joined by a contrast word, both with the same polarity."""
    connector = r"[^。！？\n]{0,10}?(?:但|但是|然而|不过|却)"
    return (
        r"(?:虽然|尽管|虽说)?[^。！？\n]{0,30}?(" + pos + r")"
        + connector + r"[^。！？\n]{0,30}?(" + pos + r")"
        r"|(?:虽然|尽管|虽说)?[^。！？\n]{0,30}?(" + neg + r")"
        + connector + r"[^。！？\n]{0,30}?(" + neg + r")"
    )


def R(rid, severity, langs, category, pattern, why, fix,
      min_count=1, max_per_1000=None, dedupe_with=None):
    return {
        "id": rid,
        "severity": severity,
        "langs": langs,
        "category": category,
        "pattern": pattern,
        "why": why,
        "fix": fix,
        "min_count": min_count,
        "max_per_1000": max_per_1000,
        "dedupe_with": dedupe_with or [],
    }


RULES = [
    # ---------------------------------------------------------------- 词汇
    R("zh-buzz-corp", "block", ["zh"], "黑话",
      r"赋能|抓手|闭环|颗粒度|拉通|组合拳|护城河|飞轮效应|第二曲线|底层逻辑|顶层设计|价值锚点|认知升级|长期主义|生态位|全链路|降本增效|提质增效|战略定力",
      "这些词不指向可观察的动作或结果，只暗示说话人的身份。",
      "写谁对谁做了什么，省了多少钱、多少时间，结果是什么。"),

    R("zh-buzz-empty", "block", ["zh"], "黑话",
      r"全方位|多维度|多角度|立体化|深层次|高水平|高质量发展|新质生产力|一站式|无缝(?:衔接|对接|体验|集成)|全场景|全周期|全景式",
      "范围词把话说满，却不给出边界；读者无法据此做任何判断。",
      "给出适用范围和排除项，或者直接删掉。"),

    R("zh-buzz-align", "warn", ["zh"], "黑话",
      r"对齐(?:一下|认知|目标|预期|口径|战略)|沉淀(?:下来|出|为|到)|复盘(?:一下|总结)?",
      "职场黑话的轻度形态；在排版、化学等语境里可能是正常词。",
      "能换成“确认”“定下来”“总结”就换；不能就保留并说明语境。",
      min_count=2, max_per_1000=0.8),

    R("zh-grand-opening", "block", ["zh"], "篇章",
      r"在这个.{0,15}(?:时代|世界|社会)|随着.{0,25}(?:的(?:快速|飞速|不断|持续))?(?:发展|进步|普及|到来)|在当今(?:社会|时代|世界)|众所周知|毋庸置疑|不可否认|显而易见|自古以来",
      "用时代做主语，具体的人和事就不用出现了。",
      "从一个具体场景、一个数字或一件刚发生的事开始。"),

    R("zh-summary-closer", "block", ["zh"], "篇章",
      r"综上所述|总而言之|总的来说|归根结底|一言以蔽之|由此可见|概言之",
      "结尾没有新信息，只是把语气往上抬。",
      "停在最后一个事实、未解决的问题或下一步动作上。",
      dedupe_with=["zh-total-then-expand"]),

    R("zh-total-then-expand", "block", ["zh"], "篇章",
      r"(?:总的来说|总体来看|整体而言|概括地说)[^。！？\n]{0,40}[。；;]\s*(?:具体(?:来说|而言|展开)|展开(?:来说|讲)|分(?:三|四|五|几)(?:点|个方面|个层面|个维度))",
      "先给总判断，再宣布要展开；结构在替代内容，读者被迫等一个已知的结论。",
      "删掉总分框架，直接写具体的那件事；需要分点就分点，不要先报幕。",
      min_count=1),

    R("zh-enumerate-frame", "warn", ["zh"], "篇章",
      r"(?:从|分)(?:三|四|五|几)个(?:方面|层面|维度|角度)(?:来|展开|说|讲)?|(?:第一|其一)[，,][^。！？\n]{1,60}(?:第二|其二)[，,]",
      "先报“分几个方面”再展开，是结构化表演；内容不需要报幕。",
      "直接写第一点；读者不需要知道总共有几点。",
      min_count=1, max_per_1000=0.5),

    R("zh-correction-opener", "block", ["zh"], "语用",
      r"(?:^|[。！？\n])\s*(?:先|首先|这里)?\s*(?:要)?\s*(?:纠正|指正|更正)(?:一下|一个)?\s*(?:观点|说法|误区|错误|你|您)?|(?:你|您)(?:这个|的)?(?:观点|说法|理解|前提|方向)(?:其实)?(?:不对|错了|有误|有偏差|站不住脚)|(?:你|您)说的(?:不对|错了|有误|有偏差)|(?:你|您)(?:错|不对)(?:了)?|我(?:不同意|不认同)(?:你|您)|(?:其实|事实上)[，,]?\s*不是这样",
      "一上来就判用户对错，把任务变成辩论；用户要的是服务，不是被纠错。",
      "先做任务。需要指出问题时，把问题写成约束、数据或后果，放在回答里，并给选项。",
      min_count=1),

    R("zh-reassurance", "block", ["zh"], "语用",
      r"主动权(?:始终|永远|一直)?(?:在|属于)(?:你|您)|(?:你|您)(?:可以|能|可)(?:随时|永远|一直)?(?:修改|调整|接管|停|回退|改)|(?:你|您)?(?:随时|永远|一直)(?:可以|能|可)?(?:修改|调整|接管|停|回退|改)|最终(?:决定权|选择权)(?:在|属于)(?:你|您)|一切(?:由|听)(?:你|您)(?:决定|安排)",
      "过度安抚：把用户本来就有、也随时能行使的控制权再说一遍，像在哄人。",
      "删掉授权句。写清做了什么、没做什么、风险是什么、下一步需要谁决定。",
      min_count=1),

    R("zh-comfort", "warn", ["zh"], "语用",
      r"(?:请|你|您)(?:放心|别担心|不用担心|不必担心)|不(?:用|必|需要)着急|慢慢来|(?:我|我们)(?:会)?(?:一直)?等你(?:确认|回复|决定)?|这只是(?:一个)?建议|仅供(?:参考|选择)|(?:随时|尽管)(?:告诉|联系|找)我|(?:无需|不用)(?:担心|害怕|顾虑)",
      "安慰话术替代了具体的下一步；读者得到情绪，得不到信息。",
      "删掉安慰，直接说决定、风险或下一步。",
      min_count=1, max_per_1000=0.6),

    R("zh-code-permission", "warn", ["zh"], "语用",
      r"(?:可按需|可自行|根据需要|视情况)(?:修改|调整|删改|使用)|(?:修改|调整)成你(?:需要|想要)的",
      "代码注释里的授权句不描述行为，只占位置；半年后没人知道这段代码的约束。",
      "注释写行为、约束、原因和坑；不要写“可按需修改”。",
      min_count=1, max_per_1000=0.5),

    R("zh-chatbot-tail", "block", ["zh"], "客服腔",
      r"希望(?:这|以上|本文|这些|我的回答|本回答).{0,15}(?:对你有帮助|有所帮助|能帮到你)",
      "聊天机器人的对话残留，不是交付物的一部分。",
      "删。交付物结束在内容上。"),

    R("zh-polite-tail", "warn", ["zh"], "客服腔",
      r"如有(?:任何)?(?:疑问|问题|需要).{0,15}(?:随时|欢迎)|欢迎随时(?:交流|联系|告诉我|找我)|如果(?:你|您)需要.{0,8}(?:告诉我|联系我)",
      "商务邮件里是礼貌，文章和文档里是客服腔。",
      "邮件保留一句；其他文体删掉。"),

    R("zh-signpost", "block", ["zh"], "篇章",
      r"让我们(?:一起)?(?:深入|来|一起)?(?:探讨|看看|聊聊|了解|走进)|话不多说|闲言少叙|直接上(?:结论|干货)|你可能会问|读到这里|看到这里|接下来(?:我们|让我)(?:来|一起)?(?:看看|聊聊|探讨)",
      "作者在描述文章，而不是写文章；读者被迫看导航。",
      "删掉导航句，让结构自己说话。"),

    R("zh-meta-article", "warn", ["zh"], "篇章",
      r"本文将|本文(?:旨在|试图|主要)|在这篇文章(?:中|里)|接下来我们(?:将|会)|以上(?:就是|是)全部",
      "元评论在解释内容，不提供内容；学术写作里有时是必要的。",
      "学术论文保留；其他文体删掉，直接进入内容。",
      min_count=1, max_per_1000=0.5),

    R("zh-ceremony", "block", ["zh"], "空话",
      r"为.{1,25}(?:提供|奠定|注入)(?:了)?(?:坚强|坚实|强有力|有力)(?:的)?(?:保障|支撑|基础|动力)|(?:注入|增添)(?:了)?(?:新|强劲)?(?:的)?(?:动能|活力)|按下.{0,8}加速键|跑出.{0,8}加速度|(?:绘就|谱写).{0,10}(?:新)?(?:画卷|篇章|华章)|再上(?:一个)?新?台阶",
      "仪式性语言在替代事实：没有数字，只有气势。",
      "删掉整个比喻，换成可核验的进展或结果。"),

    R("zh-worth-thinking", "block", ["zh"], "空话",
      r"值得我们(?:深思|思考)|引发(?:了)?(?:广泛|热烈|高度)(?:关注|讨论|反响)|值得(?:我们)?(?:关注|警惕)的是",
      "“值得深思”通常意味着作者还没想清楚。",
      "写出你的判断，或者承认这里没有结论。"),

    R("zh-pseudo-profound", "warn", ["zh"], "空话",
      r"(?:是|成为).{1,12}的(?:语言|镜子|底色|注脚|隐喻|通行证|入场券|解药)|.{0,12}的尽头是|真正.{0,8}的.{0,8}，是",
      "可复用的格言公式，听起来深，实际不增加精度。",
      "把比喻拆开，直接说两者的具体关系。",
      max_per_1000=0.6),

    # ---------------------------------------------------------------- 句式
    R("zh-negative-escalation", "warn", ["zh"], "逻辑",
      r"(?:不是|并非|不仅)[^。！？\n]{1,30}而是|与其说[^。！？\n]{1,20}不如说|[^。！？\n]{1,25}[，,]\s*(?:而)?不是[^。！？\n]{1,25}",
      "先检查 A 是否是读者真会误认的选项；A 不合理，否定就是稻草人。两个方向都算：不是 A 而是 B，以及 B 而不是 A。",
      "A 成立就保留；不成立就删掉否定，直接说 B。B 是事实、A 是常见误说时，保留。",
      min_count=1,
      dedupe_with=["zh-important-frame", "zh-forced-elevation",
                   "zh-plain-fact-denial", "zh-reframe-fact",
                   "zh-euphemism", "fic-not-but"]),

    R("zh-euphemism", "block", ["zh"], "逻辑",
      r"价值(?:的)?重新分配|结构性调整|战略聚焦|组织优化|人员优化",
      "用管理术语替代事实：下降、亏损、裁员被说成结构调整。",
      "先用事实的名字，再解释原因和范围。",
      min_count=1, dedupe_with=["zh-plain-fact-denial"]),

    R("zh-analogy-escalation", "block", ["zh"], "语用",
      r"与其说[^。！？\n]{1,20}(?:，|,)\s*(?:更|倒)?(?:像|是)|比起[^。！？\n]{1,25}(?:，|,)\s*(?:它|这|那)?\s*(?:更|反而|倒)?(?:像|是)|(?:就像|像是|好比)[^。！？\n]{1,35}(?:，|,)\s*(?:而)?不只是",
      "用类比抬价：借一个更高级的意象，把普通东西抬到它没有证据的位置。",
      "写具体行为或数字；类比最多一个，不要接‘而不只是’。",
      min_count=1),

    R("zh-redundant-negation", "warn", ["zh"], "逻辑",
      r"(?:不是|并非)[^。！？\n]{1,25}(?:而是|，是)[^。！？\n]{0,20}(?:然后|接着|随后|就)[^。！？\n]{0,12}(?:吃|啃|喝|打开|按|走|跑|笑|哭)",
      "后面的动作已经把答案演出来了，前面的否定是多余的；读者被解释了一遍自己刚看懂的事。",
      "删掉否定和解释，直接写动作。",
      min_count=1),

    R("zh-pseudo-technical-b", "warn", ["zh"], "逻辑",
      r"(?:不是|并非)[^。！？\n]{1,25}(?:而是|，是)[^。！？\n]{0,20}(?:预训练|对齐|多模态|异构|范式|底座|中台)",
      "B 端堆了技术术语，A 又不合理；句子在展示词汇量，不在说清东西。",
      "把 B 还原成具体名词或动作；技术术语只在描述技术对象时使用。",
      min_count=1),

    R("zh-forced-elevation", "block", ["zh"], "语用",
      r"(?:不是|并非)[^。！？\n]{1,25}(?:而是|，是)[^。！？\n]{0,12}(?:灵魂|星河|宇宙|银河|宿命|史诗|文明|时代|历史|命运|救赎|觉醒|隐喻|诗|远方|洪流|浪潮|深渊|情绪|认知)",
      "把具体动作或事实硬抬成宏大抽象，用气势替代信息；读者不知道到底发生了什么。",
      "先写 1 就是 1：谁做了什么、结果是什么。要比喻就只用一个，并且贴着机制。",
      min_count=1, dedupe_with=["zh-plain-fact-denial"]),

    R("zh-cosmic-simile", "block", ["zh"], "语用",
      r"(?:犹如|宛如|仿佛|像是|好似)[^。！？\n]{0,20}(?:星河|宇宙|银河|星辰|史诗|洪流|浪潮|历史|命运|灵魂|深渊|烈火|光芒)",
      "用宇宙级意象给普通场面加冕；画面越大，信息越少。",
      "删掉比喻，写清动作、位置、结果；或者只保留一个能被验证的细节。",
      min_count=1, dedupe_with=["zh-grand-simile"]),

    R("zh-grand-simile", "block", ["zh"], "语用",
      r"(?:就像|像是|仿佛|犹如|宛如|好似|好比|像|无异于|堪比)[^。！？\n]{0,30}(?:帝国|战场|沙盘|棋局|棋手|交响|乐章|史诗|洪流|巨轮|引擎|灯塔|钥匙|桥梁|基因|血液|心脏|灵魂|操作系统|护城河|飞轮|星辰|宇宙|星河|风暴|浪潮|战争|将军|魔术|炼金|登月|巨龙)",
      "比喻的载体和本体对不上：宏大意象没有对应任何机制，只是在加戏。",
      "删掉比喻；要留就写出两个具体对应点，或者换成规模、成本、耗时。",
      min_count=1, dedupe_with=["zh-cosmic-simile"]),

    R("zh-hyperbole", "warn", ["zh"], "语用",
      r"无异于|堪比|不亚于|足以(?:改变|颠覆|重塑|决定)|彻底(?:改变|颠覆|重塑)|重新定义",
      "用尺度词替代证据：换心脏、登月、重新定义，都没有可核对的量级。",
      "换成规模、成本、耗时或前后对比。",
      min_count=1, max_per_1000=0.8,
      dedupe_with=["zh-rainbow-fart", "zh-grand-simile"]),

    R("zh-grand-abstraction", "warn", ["zh"], "词汇",
      r"(?:灵魂|情绪|认知|价值|生命|命运|时代|文明|历史)(?:的)?(?:解读|切换|重构|重估|觉醒|救赎|隐喻|注脚|回响|底色|升华)",
      "把日常动作包装成抽象命题；听起来深，实际没有可验证的内容。",
      "改成具体动作或结果：听歌就是换了一首，读书就是读完了哪一章。",
      min_count=1,
      dedupe_with=["zh-forced-elevation"]),

    R("zh-plain-fact-denial", "block", ["zh"], "逻辑",
      r"这不是(?:下降|增长|亏损|失败|事故|裁员|延期|错误)[^。！？\n]{0,15}(?:而是|，是)[^。！？\n]{0,15}",
      "拒绝用事实的名字称呼事实，换成抽象概念；读者不知道到底是下降、亏损还是延期。",
      "1 就是 1。先把数值、对比和原因写出来，再谈解释。",
      min_count=1),

    R("zh-reframe-fact", "warn", ["zh"], "逻辑",
      r"这不是(?:数据|问题)[^。！？\n]{0,15}(?:而是|，是)[^。！？\n]{0,15}",
      "把事实问题改写成概念问题；有时是澄清，有时是在回避具体口径。",
      "如果只是分类，直接说分类标准；如果是下降/亏损，先给数字。",
      min_count=1,
      dedupe_with=["zh-negative-escalation"]),

    R("zh-important-frame", "block", ["zh"], "逻辑",
      r"(?:真正|其实|事实上|说到底)?(?:重要|关键|核心|重点)的?(?:地方|问题|一点|部分|是)?(?:不在|不是)[^。！？\n]{1,35}(?:，|,)?\s*(?:而)?(?:在|是)[^。！？\n]{1,35}",
      "先宣布什么最重要，再否定一个稻草人；读者被迫等结论，作者显得在给人生上课。",
      "直接说重点和它的后果。不要替读者规定什么重要，也不要用“不在 A 而在 B”的对仗。",
      min_count=1),

    R("zh-fake-contrast", "warn", ["zh"], "逻辑",
      _same_polarity(_POSITIVE_TRAIT, _NEGATIVE_TRAIT),
      "前后两个角度同向，却用转折词制造反差；读者等一个反转，只等到同义反复。",
      "删掉转折词，读出真实关系：并列、递进、因果、解释。只有真的相反、相抵或超出预期才保留转折。",
      min_count=1),

    R("zh-but-means", "warn", ["zh"], "逻辑",
      r"(?:但|但是|然而|不过)[，,]?\s*(?:这)?也?意味着|(?:但|但是|然而|不过)[^。！？\n]{0,6}(?:更重要的是|关键在于|真正的问题是)",
      "“但这也意味着”引入的是结果或补充，不是反转；转折词在这里只是节奏。",
      "改成“这意味着”“更重要的是”，或者直接说下一句。",
      min_count=1),

    R("zh-transition-elaboration", "warn", ["zh"], "逻辑",
      r"(?:然而|但是|但|不过|可是)[^。！？\n]{0,12}(?:也就是说|换句话说|同样|也是如此|更是如此)",
      "转折词后面接的是解释或同义复述，不是相反的角度。",
      "删掉转折词；如果只是重复，连后半句一起删。",
      min_count=1),

    R("zh-rainbow-fart", "block", ["zh"], "语用",
      r"堪称|简直是|可谓是|封神|天花板|YYDS|绝绝子|炸裂|史诗级|神级|无人能及|天下第一|吊打|碾压|完美(?:无瑕|收官|解决)|令人(?:惊叹|震撼|窒息)",
      "形容词通货膨胀：用最高级替代证据，读者只知道作者很激动。",
      "换成一个可核验的比较、数字或具体行为；给不出就删。",
      min_count=1),

    R("zh-superlative", "warn", ["zh"], "语用",
      r"惊艳|颠覆(?:性)?|顶级(?!域名)|最强",
      "最高级词在文案里通常是情绪，不是事实；部分语境可能是术语。",
      "能换成对比就换；不能就说明适用范围。",
      min_count=1, max_per_1000=0.5),

    R("zh-defensive-humble", "warn", ["zh"], "语用",
      r"(?:只是|只不过|仅仅是)[^。！？\n]{1,25}(?:，|,)\s*(?:而)?不是|(?:只能|仅能)[^。！？\n]{1,25}(?:，|,)\s*(?:还|尚)?未|(?:还|尚)未[^。！？\n]{1,20}(?:，|,)\s*(?:但|不过|然而)",
      "用自贬换取宽容：把限制写成需要被原谅的戏，读者被迫安慰作者。",
      "直接写范围、原因、下一步；局限本身不是问题，防御姿态才是。",
      min_count=1, max_per_1000=0.6),

    R("zh-flattery", "warn", ["zh"], "语用",
      r"(?:您|你)(?:真的|简直|实在)?(?:太|很|非常)(?:棒|厉害|优秀|专业|有眼光)|像(?:您|你)这样(?:有|的)(?:远见|眼光|品位|专业)",
      "对读者的彩虹屁会稀释请求，读者先被夸，再被要求。",
      "删掉夸奖，直接说你要他做什么、为什么是他。",
      min_count=1, max_per_1000=0.5),

    R("zh-notonly", "warn", ["zh"], "句式",
      r"不仅[^。！？\n]{1,35}(?:更|还|也)(?:是|要|能|在|让|会|有)",
      "后半句常被强行说成“更重要”，其实只是并列。",
      "留下信息量大的那一半，或者拆成两句。",
      min_count=2, max_per_1000=0.8),

    R("zh-enum-formula", "warn", ["zh"], "句式",
      r"首先[，,].{0,250}?其次[，,].{0,250}?(?:最后|最终|再者)[，,]",
      "三拍结构是演讲节奏，不是信息结构；常有一个是填充。",
      "按真实顺序写，有几项写几项。",
      min_count=1),

    R("zh-hedge", "warn", ["zh"], "句式",
      r"某种程度上|在一定程度上|从某种意义上(?:说|讲)|不得不(?:说|承认)|客观(?:地)?(?:说|讲)|需要(?:指出|强调|注意)的是|值得注意的是|值得一提的是|不难(?:发现|看出)|可以说",
      "限定词在保护作者，不在帮助读者。",
      "删掉；如果确实不确定，给出范围和触发条件。",
      min_count=2, max_per_1000=0.8),

    R("zh-filler-verb", "warn", ["zh"], "句式",
      r"进行(?:了)?(?:分析|优化|调整|处理|评估|梳理|复盘|升级|改造|整合|部署|实施|推进|论证)|通过.{1,20}的(?:方式|手段|方法)|对于.{1,15}而言|在.{1,15}方面",
      "名词化让句子变长，责任人消失；中文本来可以直接用动词。",
      "还原动词：“对代码进行了优化”改成“改了代码”。",
      min_count=2, max_per_1000=1.2),

    R("zh-empty-claim", "warn", ["zh"], "空话",
      r"(?:取得|实现)(?:了)?(?:显著|重要|突破性|阶段性|长足)(?:的)?(?:成果|进展|成效|突破)|(?:具有|有着)(?:重要|深远|积极|重大)(?:的)?(?:意义|影响|作用)|(?:发挥|起到)(?:了)?(?:重要|关键|积极)(?:的)?作用",
      "没有基准和数字的“显著”，等于没说。",
      "给出前后对比、时间窗口和口径。",
      min_count=1, max_per_1000=0.4),

    R("zh-inflate-adverb", "warn", ["zh"], "词汇",
      r"(?:极大|显著|全面|有效|持续|深入|充分|大幅|有力|快速)地?(?:提升|优化|推动|促进|增强|改善|解决|保障|支撑|激发|释放)",
      "程度副词在没有基准时只是音量。",
      "换成差值、比例或具体动作。",
      min_count=2, max_per_1000=1.5),

    R("zh-hollow-adj", "warn", ["zh"], "词汇",
      r"(?:强大|丰富|多样|灵活|便捷|高效|优质|先进|领先|卓越|全面|深度|立体|多元|强劲|完善|成熟)的?(?:能力|方案|体验|服务|支持|保障|体系|平台|生态|功能)",
      "形容词不提供可验证信息，读者无法用它做判断。",
      "给数、给场景、给对比。",
      min_count=2, max_per_1000=1.5),

    R("zh-passive", "warn", ["zh"], "句式",
      r"被(?:认为|视为|称为|誉为|广泛(?:认为|关注|应用|使用))",
      "施动者消失，责任也跟着消失。",
      "补上谁认为、谁使用；补不上就删。",
      min_count=2, max_per_1000=1.0),

    R("zh-is-de", "warn", ["zh"], "句式",
      r"是[^。！？\n]{1,20}的(?:重要|关键|核心|基础|前提|保障|体现|缩影|基石)",
      "“是……的”强调句把判断包装成常识。",
      "直接说它重要在哪，或者删掉。",
      min_count=2, max_per_1000=1.0),

    R("zh-one-of", "hint", ["zh"], "词汇",
      r"之一",
      "“之一”把结论稀释成无法反驳的空话。",
      "给排序、范围或具体对象。",
      min_count=3, max_per_1000=2.0),

    R("zh-de-chain", "hint", ["zh"], "机械",
      r"[\u4e00-\u9fa5]{0,4}的[\u4e00-\u9fa5]{0,4}的[\u4e00-\u9fa5]{0,4}的",
      "连续三个以上的“的”，句子读起来打结。",
      "拆句，或把中心词提前。",
      min_count=1),

    R("zh-four-char-stack", "hint", ["zh"], "机械",
      r"(?:[\u4e00-\u9fa5]{2}、){3,8}[\u4e00-\u9fa5]{2}",
      "四字格堆叠自带公文节奏，容易掩盖主谓宾。",
      "留一个，其余改成动词短句。",
      min_count=1),

    R("zh-fake-source", "warn", ["zh"], "事实",
      r"(?:数据|研究|调查|报告|统计)(?:显示|表明|指出|发现|证明)[^。！？\n]{0,40}(?:显著|大幅|明显|超过|高达|提升|下降)",
      "数字借用了研究的权威，却没有承担被核查的风险。",
      "给出机构、年份、样本量和链接；找不到就删掉数字。",
      min_count=1),

    R("zh-authenticity-marker", "warn", ["zh"], "词汇",
      r"真正(?:的|地)?|真真正正|名副其实|货真价实|实打实|属实|真实(?:环境|数据|场景|体验|世界|可用|有效|落地|需求)|真切",
      "用“真正/真实/属实”声明可信，而不是给证据；读者会反问：难道还有假的？",
      "删掉标记，给来源、环境、样本或日期。确实需要区分真实/合成时，写明两边。",
      min_count=1, max_per_1000=0.8, dedupe_with=["zh-important-frame"]),

    R("zh-zero-config", "warn", ["zh"], "事实",
      r"(?:无需|不用|不需要|免)(?:配置|部署|培训|安装)|零配置|开箱即用",
      "零配置是产品承诺，不是事实；它掩盖了账号、权限或迁移成本。",
      "写出实际需要的那一步和耗时；确实为零再保留，并说明边界。",
      min_count=1, max_per_1000=0.5),

    R("zh-vague-social-proof", "warn", ["zh"], "事实",
      r"(?:有|不少|很多|大量|众多)(?:的)?(?:团队|企业|公司|用户|客户)(?:已经|正在)?(?:在)?(?:用|使用|选择|采用)",
      "模糊的社会证明：没有样本、时间、来源，读者无法核对。",
      "给客户名、数量、时间和口径；给不出就删。",
      min_count=1, max_per_1000=0.5),

    R("zh-placeholder-copy", "warn", ["zh"], "语用",
      r"这里(?:先)?(?:不写|空着)|这部分先空着|待补充|待完善|TODO|TBD",
      "把编辑备注留在成品里，读者看到的是作者的空白，不是内容。",
      "缺失事实列在交付文本外；正文删掉占位句，或改写成对读者成立的限制说明。",
      min_count=1, max_per_1000=0.5),

    R("zh-ai-selfref", "warn", ["zh"], "语用",
      r"作为(?:一个)?(?:AI|人工智能|语言模型|大模型)|我是(?:一个)?(?:AI|人工智能|语言模型)",
      "在交付物里说明自己是 AI，通常与内容无关。",
      "删；如果必须披露，写在文末的说明里。",
      min_count=1),

    R("zh-fake-candid", "warn", ["zh"], "语用",
      r"说实话|坦白说|老实说|不客气地说|说白了|讲真|有一说一",
      "停顿再揭晓是制造出来的亲密感；真诚实的人通常直接说。",
      "删掉铺垫，直接说那件事。",
      min_count=1, max_per_1000=0.5),

    R("zh-imagine", "warn", ["zh"], "语用",
      r"想象一下|试想一下|不妨想象|让我们把目光转向",
      "要求读者想象，是在用场景替代证据。",
      "给一个真实发生过的场景。",
      min_count=1, max_per_1000=0.5),

    R("zh-rhetorical", "warn", ["zh"], "句式",
      r"为什么(?:呢)?[？?].{0,30}(?:因为|答案)|难道不是|你有没有(?:想过|发现)",
      "自问自答把单人独白伪装成对话，读者并没有问。",
      "直接给结论和依据。",
      min_count=1, max_per_1000=0.4),

    R("zh-one-to-many", "block", ["zh"], "句式",
      r"一(?:个|次|套|键|处)[^。！？\n]{1,15}[，,]\s*(?:多(?:个|种|处)(?:场景|系统|业务|部门|渠道|门店|角色|层级|端|平台|设备|终端)|多处(?:生效|部署|复用|落地|同步)|全部(?:搞定|打通|覆盖|生效|接入)|各处(?:生效|同步)|人人(?:可用|能用))[^。！？\n]{0,15}",
      "用“一”对“多”的数目包装制造规模感，但一和多都没有边界；和堆叠定语同源。",
      "写清一个具体对象和它实际覆盖的数量、范围；给不出就删掉包装。",
      min_count=1),

    R("zh-stacked-modifiers", "block", ["zh"], "句式",
      r"[可有无能会支持具备高低全多易难更最][^，。；、\n]{0,12}[、，][可有无能会支持具备高低全多易难更最][^，。；、\n]{0,12}[、，][可有无能会支持具备高低全多易难更最][^，。；、\n]{0,12}的\s*[\u4e00-\u9fa5A-Za-z0-9]{1,12}",
      "三个以上同构定语在名词前打鼓，用节奏冒充功能密度；每一项都没有证据。",
      "只留最要命的那一项，写成主谓句并给证据；其余删掉或放进参数表。",
      min_count=1),

    R("zh-stacked-modifiers-generic", "warn", ["zh"], "句式",
      r"[^，。；！？\n、]{1,12}[、，][^，。；！？\n、]{1,12}[、，][^，。；！？\n、]{1,12}的\s*[\u4e00-\u9fa5A-Za-z0-9]{1,12}",
      "三项以上定语连排，可能是真实枚举，也可能是功能堆叠的节奏。",
      "真实枚举保留；如果是功能罗列，留一项并给证据。",
      min_count=1, dedupe_with=["zh-stacked-modifiers"]),

    R("zh-fake-range", "hint", ["zh"], "句式",
      r"从.{2,15}到.{2,15}，?(?:再到|以及).{2,15}",
      "范围两端不在同一尺度上时，只是听起来完整。",
      "列出真实覆盖的对象。",
      min_count=1),

    R("zh-slogan", "warn", ["zh"], "空话",
      r"(?:让|使).{1,15}(?:更|变得)(?:美好|简单|高效|智能|自由|从容)",
      "品牌口号式收束，通常没有可执行内容。",
      "写清楚为谁省掉了哪一步。",
      min_count=1, max_per_1000=0.5),

    R("zh-mini-theater", "block", ["zh"], "语用",
      r"你[^。！？\n]{0,15}[，,]\s*(?:(?:它|系统|平台|页面|应用|报表)\s*(?:立刻|马上|瞬间|秒|自动|就)|(?:立刻|马上|瞬间|秒|一键|自动)[^。！？\n]{0,10})",
      "第二人称加即时反应，把一次操作写成舞台剧，用零摩擦的错觉替代真实延迟和条件。",
      "写清点击之后发生什么、等多久、失败怎么办；不要用“立刻回应”替代延迟说明。",
      min_count=1),

    R("zh-instant-formula", "block", ["zh"], "句式",
      r"只要[^。！？\n]{1,25}[，,]\s*(?:就|便)?\s*(?:立刻|马上|瞬间|一秒|秒|立等)[^。！？\n]{0,12}",
      "“只要……立刻……”把条件和结果压成一句广告，省略了配置、等待和失败。",
      "给出真实的前置条件和耗时；做不到就删掉“立刻”。",
      min_count=1),

    R("zh-zero-friction", "warn", ["zh"], "空话",
      r"(?:不用|无需|不需要)[^。！？\n]{1,20}[，,、]\s*(?:也)?(?:不用|无需|不需要)[^。！？\n]{0,15}",
      "连续否定成本，读者只听到“没有代价”，听不到代价是什么。",
      "写出实际需要的一步和它的成本；零摩擦通常不成立。",
      min_count=1, max_per_1000=0.8),

    R("zh-trend-hype", "block", ["zh"], "篇章",
      r"未来已来|大势所趋|不可(?:逆转|阻挡)的(?:趋势|潮流)|下一个风口|站在风口|时代(?:的)?浪潮|历史的(?:车轮|潮流)",
      "用时代趋势给结论加冕，没有可核验的对象。",
      "删掉趋势判断，写谁在什么时候做了什么。",
      min_count=1),

    R("zh-trend-claim", "warn", ["zh"], "篇章",
      r"越来越多的[^。！？\n]{1,15}(?:开始|正在|选择|采用)|正在成为[^。！？\n]{1,20}(?:新)?(?:趋势|标配|共识|刚需)|成为一种(?:新)?(?:趋势|潮流)",
      "“越来越多”是未统计的比较级，读者无法核对。",
      "给样本、时间和来源；给不出就删。",
      min_count=1),

    R("zh-self-elaboration", "warn", ["zh"], "语用",
      r"这意味着[^。！？\n]{1,30}|这说明[^。！？\n]{1,30}|这背后(?:是|藏着|意味着)[^。！？\n]{1,30}|换句话说|也就是说",
      "替读者把结论再说一遍，通常没有增加信息，只是在延长作者的存在感。",
      "删掉阐释句；如果结论确实需要，用一句事实代替。",
      min_count=2, max_per_1000=0.8),

    # ---------------------------------------------------------------- 标点
    R("zh-colon-list", "hint", ["zh"], "机械",
      r"[：:][^。\n]{0,80}、[^。\n]{0,80}、",
      "冒号加三项并列是 AI 的高频排版习惯。",
      "并列项确实并列就保留；不是就写成句子。",
      min_count=1, max_per_1000=3.0),

    R("zh-ascii-punct", "hint", ["zh"], "机械",
      r"[\u4e00-\u9fa5][,;:!?]",
      "中文里混用半角标点。",
      "改成全角标点。",
      min_count=2, max_per_1000=3.0),

    R("zh-spacing", "hint", ["zh"], "机械",
      r"[\u4e00-\u9fa5][A-Za-z]|[A-Za-z][\u4e00-\u9fa5]",
      "中英文之间没有空格，排版会挤。",
      "加一个空格；品牌名等固定写法除外。",
      min_count=3, max_per_1000=5.0),

    R("zh-ellipsis", "hint", ["zh"], "机械",
      r"\.\.\.",
      "用三个半角句点代替中文省略号。",
      "改成……",
      min_count=1),

    R("zh-single-emdash", "hint", ["zh"], "机械",
      r"(?<!—)—(?!—)",
      "中文破折号是——，单个 — 多是从英文文本迁移过来的。",
      "改成——、逗号或括号。",
      min_count=1),

    R("emoji-decor", "hint", ["any"], "语用",
      r"[\U0001F300-\U0001FAFF\u2600-\u27BF\u2B00-\u2BFF]",
      "正式文本里的装饰性 emoji 不承载信息。",
      "删掉；社媒文案里如果作者本来就用，保留。",
      min_count=1),

    R("zh-announcement-opener", "block", ["zh"], "篇章",
      r"值得注意的是|需要强调的是|话说到前头|先说结论|先说一点|先讲结论|这里先说|提前说一句",
      "宣告式开场在报幕，不在说事；读者被迫等正文。",
      "删掉报幕，直接写第一句事实。",
      min_count=1),

    R("zh-concept-surgery", "block", ["zh"], "语用",
      r"(?:先|我们|让我|不妨|来)?(?:把|将)?[^。！？\n]{0,8}(?:这个词|这个概念|这个词拆开|重新定义)[^。！？\n]{0,8}|(?:拆开|拆解|重新定义)[^。！？\n]{0,10}(?:这个词|概念|定义)",
      "表演性拆词：真人不对词做手术，直接说事实。",
      "删掉拆词旁白，直接陈述定义或事实。",
      min_count=1),

    R("zh-meeting-speak", "block", ["zh"], "语用",
      r"这个问题问到点子上了|老规矩|按老规矩|我总结三点|会议纪要|三句话(?:说清|讲清)|第一句[，,].{0,60}第二句",
      "会议式编号和接话套话，把文字变成纪要。",
      "删掉套话，直接说内容。",
      min_count=1),

    R("zh-emotion-hype", "warn", ["zh"], "语用",
      r"扎心|残酷|毛骨悚然|狂飙|拉爆|破防|窒息|炸裂|封神|惊掉下巴|细思极恐",
      "夸张情绪标签替代事实和幅度；读者只感到被推着走。",
      "换成客观事实、数量或影响范围。",
      min_count=1, max_per_1000=0.8,
      dedupe_with=["zh-rainbow-fart"]),

    R("zh-superlative-zui", "warn", ["zh"], "词汇",
      r"最(?:干脆|硬核|重要|关键|核心|根本|本质|好|强|大|快|慢)",
      "“最”给不可分级的东西加冕；读者会问跟谁比。",
      "删掉“最”，或者给出比较对象和口径。",
      min_count=1, max_per_1000=1.0),

    R("zh-nominalization", "warn", ["zh"], "句式",
      r"(?:进行|做出|造成|加以|予以|给予)(?:了)?(?:分析|决定|影响|处理|评估|优化|调整|判断|说明|解释|支持|帮助|提升|改善)",
      "动词被名词化，句子变长，责任人消失。",
      "还原动词：进行分析→分析；做出决定→决定；造成影响→影响。",
      min_count=1, max_per_1000=1.5),

    R("zh-lecture-tone", "warn", ["zh"], "语用",
      r"(?:你|您)?(?:必须|务必|一定要|切记|记住)(?:要|得|做|改|注意|相信)?",
      "居高临下的指令语气，把读者当学生；除非用户明确要求命令式。",
      "改成建议或选项：不妨、可以、建议。",
      min_count=1, max_per_1000=1.0),

    R("zh-correlative-parallel", "warn", ["zh"], "句式",
      r"既[^。！？\n]{1,15}又|不仅[^。！？\n]{1,20}而且",
      "对称排比是节奏，不是信息；两项常有一项是填充。",
      "能直说就直说；只留信息量大的那一项。",
      min_count=1, max_per_1000=0.8),


    R("zh-translationese-based", "block", ["zh"], "本地化",
      r"(?:^|[。！？\n])\s*基于[^。！？\n]{1,25}[，,]\s*(?:我们|你|他|她|它|这|该|其|拆解|分析|梳理|优化|提升|打造|构建|实现|推动|解决|完成)",
      "“基于……，我们……”是英语 Based on... 的语序；中文通常先给动作或对象。",
      "把介词短语挪到后面：我们看了……，把……分成……。",
      min_count=1),

    R("zh-fronted-adverbial", "warn", ["zh"], "本地化",
      r"(?:^|[。！？\n])\s*(?:通过|作为|鉴于|关于|对于|根据)[^。！？\n]{1,30}[，,]\s*(?:我们|你|他|她|它|这|该|其|拆解|分析|梳理|优化|提升|打造|构建|实现|推动|解决|完成)",
      "句首介词短语加逗号，是英语状语前置；中文更常把条件放后面或用短句。",
      "改成“我们……，因为/根据……”或直接说动作。",
      min_count=1),

    R("zh-jargon-deconstruct", "warn", ["zh"], "本地化",
      r"拆解(?:问题|方案|需求|逻辑|目标|任务|数据|业务|流程|指标)",
      "“拆解”是咨询/技术黑话；中文日常说分析、拆开、分成几块。",
      "换成具体动作：把问题分成三块、逐项看数据。",
      min_count=1),

    R("zh-this-makes", "warn", ["zh"], "本地化",
      r"(?:^|[。！？\n])\s*这(?:使得|让)",
      "“这使得……”是 This makes... 的直译；中文常用“于是/结果/所以”。",
      "改成“于是”“结果”，或者直接写后果。",
      min_count=1),

    R("zh-as-a", "warn", ["zh"], "本地化",
      r"(?:^|[。！？\n])\s*作为(?:一个|一名|一家|一位)?[^。！？\n]{1,15}[，,]\s*(?:我们|我|你|他|她)",
      "“作为一个……，我们……”是 As a... 的直译；中文常直接说“我们公司/我”。",
      "删掉“作为”，直接给身份或动作。",
      min_count=1),

    R("zh-perspective", "warn", ["zh"], "本地化",
      r"从[^。！？\n]{1,15}的(?:角度|视角|层面)(?:来看|来说|看|讲)",
      "“从……的角度来看”是 From the perspective of... 的直译；中文可直说“对……来说”。",
      "改成“对用户来说”或直接说判断。",
      min_count=1),


    R("zh-incident-theater", "block", ["zh"], "语用",
      r"(?:当前|目前)(?:所有|全部)(?:的)?[^。！？\n]{0,6}(?:进程|任务|流程|管线)(?:都)?(?:已)?(?:停止|暂停|中断)|下一步(?:只|仅)做(?:恢复|回滚|修复)|实际验收|菜谱边界",
      "把普通修改写成事故报告：进程停止、只做恢复、不会覆盖；读者只看到流程表演。",
      "1-3 句说清改了什么、撤回了什么、怎么确认；不写恢复计划。",
      min_count=1),

    R("zh-process-jargon", "warn", ["zh"], "语用",
      r"任务边界|范围约束|恢复计划|回滚方案|变更清单|验收标准|只做恢复|不擅自",
      "流程术语堆在普通任务上，显得像事故演练；读者不知道实际改了什么。",
      "换成动作：改了哪一处、撤回了哪一处、怎么确认。",
      min_count=1, max_per_1000=1.0),

    R("zh-recovery-plan", "warn", ["zh"], "语用",
      r"(?:^|\n)\s*[1-9][.、]\s*(?:完整保留|从当前|实际验收|更新(?:规则|菜谱|文档|约束)|去掉)",
      "为一个简单撤销写多步恢复计划；步骤越多，越像在表演谨慎。",
      "直接撤销，给 diff 或一句确认；真事故再写复盘。",
      min_count=1),

    R("zh-overpromise", "warn", ["zh"], "语用",
      r"(?:我)?(?:不会|不再|绝不)(?:擅自|主动)?(?:覆盖|修改|删除|添加|碰)",
      "先承诺不碰，再继续操作；承诺不是信息，范围和命令才是。",
      "说清楚要改哪个文件、哪一段；不要用保证替代说明。",
      min_count=1, max_per_1000=0.8),


    R("zh-progress-narration", "warn", ["zh"], "语用",
      r"分析中|检查中|验证中|核验中|考虑边界情况|实施安全措施|马上就好|稍等片刻|正在处理|正在分析|正在检查|正在验证",
      "状态词刷屏，用户看不到结果；时间在走，任务没动。",
      "做完再说；阻塞时只说缺什么、下一步、何时回来。",
      min_count=3),

    R("zh-unverified-constraint", "warn", ["zh"], "逻辑",
      r"(?:尚未|还没有|未)(?:验证|确认|测试)[^。！？\n]{0,25}(?:是否|能否|够不够|装得下|容量|边界|失败)",
      "可验证的约束被写成免责声明；先验证，再报告。",
      "做那个检查；不能做就说缺什么。",
      min_count=1),

    R("zh-time-narration", "warn", ["zh"], "语用",
      r"(?:连续)?(?:工作|运行|分析|检查|验证|处理)了?\s*\d+\s*(?:个)?\s*(?:小时|分钟|天)",
      "时间不是进度；用户要的是结果或阻塞点。",
      "删掉耗时叙述，给结果、剩余量或下一步。",
      min_count=1),

    R("zh-negative-priming", "warn", ["zh"], "用语",
      r"(?:不要|别|禁止|严禁|避免)(?:再|去)?(?:加|放|写|提|碰|用|出现|包含|带|使用)[^。！？\n]{1,12}|(?:不含|不包含)[^。！？\n]{1,12}",
      "负向约束把 X 再强调一遍；模型对否定词和 X 都敏感，越说越容易回来。",
      "能删就删；要保留边界就写正向状态：“只包含 A”“这个函数只处理 B”。",
      min_count=1),


    R("zh-emotional-value", "warn", ["zh"], "语用",
      r"欢迎来到|希望(?:你|您)(?:喜欢|享受|用得开心|玩得开心)|祝(?:你|您)|加油|辛苦(?:了|啦)|感谢(?:你|您)的(?:阅读|时间|支持)|期待(?:与|和)?(?:你|您)|愿(?:你|您)|一起(?:加油|努力|成长)",
      "技术文档和代码注释默认只给信息；欢迎语、鸡血和祝福是情绪价值，不是内容。",
      "删掉。用户明确要求友好、教程或营销语气时，按用户。",
      min_count=1),


    R("zh-invented-opponent", "block", ["zh"], "语用",
      r"很多人以为|很多人认为|有人会说|有人会问|有些人觉得|你可能会问|你可能想问|你也许会想|你也许会觉得|不要以为|别以为|其实你不需要|其实你不用",
      "替读者造一个不存在的反对意见，再反驳它；读者没有问，作者在自问自答。",
      "删掉虚构的对手，直接说结论或动作；用户真问过，再回应。",
      min_count=1, dedupe_with=["zh-signpost"]),

    R("zh-preemptive-opener", "warn", ["zh"], "语用",
      r"^\s*(?:不是|并非|不要|别)[^。！？\n]{1,25}",
      "开头先否定一个用户没提的东西，是虚空索敌；读者不知道你在反驳谁。",
      "开头直接给任务结果；要澄清时问一个具体问题。",
      min_count=1),


    R("zh-carrying-trait", "block", ["zh"], "本地化",
      r"带着(?:一(?:丝|抹|缕|点))?不容(?:置疑|忽视|抗拒|察觉|侵犯|置喙)的[^。！？\n]{1,15}",
      "“带着一丝不容X的Y”是外语式表情描写；中文通常用副词或动作。",
      "改成动作或短句：“他邪魅一笑”“他笑了一下，眼神冷下来”。",
      min_count=1),

    R("zh-carrying-trait-generic", "warn", ["zh"], "本地化",
      r"带着(?:一(?:丝|抹|缕|点))?[^。！？\n]{0,12}的[^。！？\n]{1,12}|眼中闪过(?:一(?:丝|抹|缕))?[^。！？\n]{0,12}|嘴角(?:勾起|扬起)(?:一(?:抹|丝))?[^。！？\n]{0,12}|空气中弥漫着[^。！？\n]{0,15}",
      "“一丝/一抹/眼中闪过/嘴角勾起/空气中弥漫”是表情描写的翻译腔模板，重复率高。",
      "换成具体动作：他笑了一下、她把杯子放下、房间里有烟味。",
      min_count=1, max_per_1000=1.0, dedupe_with=["zh-carrying-trait"]),

    R("zh-stock-simile", "warn", ["zh"], "本地化",
      r"(?:如同一|宛如|就像|仿佛)(?:一)?(?:颗|块|道|片)[^。！？\n]{1,15}(?:砸进|投进|落入|坠入|掉进)[^。！？\n]{1,15}(?:里|中)",
      "“如同一颗……砸进……里”是现成比喻框架；后半句删掉涟漪，框架还在。",
      "删掉比喻，写这个动作对人物或场景的实际影响。",
      min_count=1, dedupe_with=["fic-stock-simile"]),

    # ---------------------------------------------------------------- English
    R("en-grand-opening", "block", ["en"], "opening",
      r"(?i)\b(?:in today'?s (?:fast-paced|ever-changing|modern|digital) world|in an ever-(?:evolving|changing) (?:world|landscape)|since the dawn of time|throughout history)\b",
      "The era is the subject so no person has to appear.",
      "Start with a dated event, a number, or a scene."),

    R("en-signpost", "block", ["en"], "structure",
      r"(?i)\b(?:let'?s dive (?:in|into)|here'?s what you need to know|without further ado|buckle up|let'?s explore)\b",
      "The writer announces the text instead of writing it.",
      "Delete the navigation and start with the content."),

    R("en-correction-opener", "block", ["en"], "voice",
      r"(?i)(?:^|[.!?\n])\s*(?:to correct you|let me correct (?:that|you)|you'?re wrong|that'?s (?:not right|wrong)|i disagree with you)[，,]?\s*",
      "Opening by grading the user turns the task into an argument.",
      "Do the task first. If something is wrong, state the constraint, evidence, and consequence, then offer options.",
      min_count=1),

    R("en-actually-opener", "warn", ["en"], "voice",
      r"(?i)(?:^|[.!?\n])\s*(?:actually|well[，,]?\s*actually)[，,]?\s+",
      "Sentence-initial 'actually' often signals a correction the reader did not ask for.",
      "Answer first; put the correction after the answer, framed as information.",
      min_count=1),

    R("en-reassurance", "block", ["en"], "voice",
      r"(?i)\b(?:you(?:'re| are) (?:always )?in (?:full )?control|you can (?:always )?(?:change|modify|revert|take over)|feel free to (?:modify|change|adjust|edit|tweak)|(?:it'?s|it is) (?:entirely )?your call|up to you)\b",
      "Reassurance that grants control the user already has; it reads as patronizing.",
      "State what changed, what is risky, and the exact way to undo it.",
      min_count=1),

    R("en-comfort", "warn", ["en"], "voice",
      r"(?i)\b(?:don'?t worry|no need to worry|take your time|i'?ll wait for you|just a suggestion|for reference only)\b",
      "Comfort phrases substitute for a concrete next step.",
      "Delete; state the decision or the risk instead.",
      min_count=1, max_per_1000=0.6),

    R("en-chatbot", "block", ["en"], "chatbot",
      r"(?i)\b(?:i hope this helps|hope this helps|let me know if you (?:have any questions|need anything)|feel free to reach out|would you like me to)\b",
      "Chat artifact pasted into a deliverable.",
      "Delete it; end on the content."),

    R("en-emotional-value", "warn", ["en"], "voice",
      r"(?i)\b(?:welcome to|we'?re (?:excited|thrilled|happy) to|hope you (?:enjoy|like|love)|happy coding|you got this|thank you for reading|thanks for reading|can'?t wait to|let'?s build|we'?re here to help)\b",
      "Technical docs and code comments default to information only; greetings and cheerleading are emotional value, not content.",
      "Delete it. Match a friendly, tutorial, or marketing tone only when the user asks for it.",
      min_count=1),

    R("en-authenticity-marker", "warn", ["en"], "vocabulary",
      r"(?i)\b(?:truly|genuinely|authentic(?:ity)?|real-world|real data|real users|production-ready|battle-tested|actually works|the real thing)\b",
      "Authenticity markers assert credibility instead of showing it.",
      "Delete the marker; name the source, environment, sample, or date.",
      min_count=1, max_per_1000=1.0),

    R("en-buzz", "warn", ["en"], "vocabulary",
      r"(?i)\b(?:delve|leverage|unlock|elevate|empower|foster|seamless|robust|cutting-edge|game-changer|revolutionize|next-level|world-class|industry-leading|best-in-class|synergy|holistic|tapestry|testament|paradigm shift)\b",
      "These words signal intent to impress rather than inform.",
      "Name the action and its result.",
      min_count=2, max_per_1000=2.0),

    R("en-inflate", "warn", ["en"], "vocabulary",
      r"(?i)\b(?:significantly|substantially|dramatically|comprehensively|effectively|seamlessly)\b",
      "An adverb without a baseline is volume, not evidence.",
      "Give the before and after numbers.",
      min_count=2, max_per_1000=2.0),

    R("en-negparallel", "warn", ["en"], "syntax",
      r"(?i)\b(?:not just .{1,60}?, (?:it'?s|they'?re|we'?re|this is)|not only .{1,60} but also)\b",
      "A formula that manufactures emphasis whether or not it is earned.",
      "State the second half directly.",
      min_count=1),

    R("en-hedge", "warn", ["en"], "syntax",
      r"(?i)\b(?:it'?s worth noting|it is important to note|needless to say|at the end of the day|when it comes to|in terms of)\b",
      "Filler that delays the claim.",
      "Delete it or state the actual scope.",
      min_count=2, max_per_1000=1.5),

    R("en-aphorism", "warn", ["en"], "syntax",
      r"(?i)\b(?:is the language of|is the currency of|is a testament to|speaks volumes|the future of)\b",
      "A reusable formula that sounds profound without adding precision.",
      "Say what the two things actually do to each other.",
      min_count=2, max_per_1000=1.0),

    R("en-fakecandid", "warn", ["en"], "voice",
      r"(?i)\b(?:honestly|here'?s the thing|real talk|let'?s be honest)\b",
      "Manufactured intimacy before an ordinary point.",
      "Just say the point.",
      min_count=1, max_per_1000=0.6),

    R("en-imagine", "warn", ["en"], "voice",
      r"(?i)\b(?:imagine a world|picture this|consider this)\b",
      "Asking the reader to imagine substitutes for evidence.",
      "Use a real example.",
      min_count=1, max_per_1000=0.5),

    R("en-closer", "warn", ["en"], "structure",
      r"(?i)\b(?:in conclusion|to sum up|all in all|the key takeaway|ultimately)\b",
      "A closing that restates instead of landing.",
      "End on the last fact or the open problem.",
      min_count=1, max_per_1000=1.0),

    R("en-transition", "warn", ["en"], "structure",
      r"(?i)\b(?:moreover|furthermore|additionally|that said|having said that)\b",
      "Connectors often claim a relation the sentences do not have.",
      "Delete; let the facts carry the relation.",
      min_count=3, max_per_1000=2.0),

    R("en-emdash", "warn", ["en"], "punctuation",
      r"—",
      "A single em dash is fine; a cluster is a machine tell.",
      "Use a period, comma, colon, or parentheses.",
      min_count=2, max_per_1000=1.0),

    R("en-corporate", "hint", ["en"], "vocabulary",
      r"(?i)\b(?:utilize|facilitate|optimize|streamline|enhance|implement)\b",
      "Latinate verbs inflate a sentence that a shorter verb would carry.",
      "Use the shorter verb when it means the same thing.",
      min_count=3, max_per_1000=4.0),

    # ---------------------------------------------------------------- 日本語
    R("ja-not-but", "warn", ["ja"], "論理",
      r"[^。\n]{1,20}ではなく[、,]?\s*[^。\n]{1,20}",
      "「AではなくB」は、Aが読者の想定や前文にないと、否定だけが浮きます。",
      "Aが前文かユーザー入力にあるか確認。なければBだけ書きます。",
      min_count=1),

    R("ja-not-only", "warn", ["ja"], "構文",
      r"だけでなく|のみならず|ばかりか",
      "対比の定型です。後半が本当に重要でなければ、片方だけ残します。",
      "情報量の多い方だけ書くか、二文に分けます。",
      min_count=1),

    R("ja-hedge", "warn", ["ja"], "構文",
      r"と言えるでしょう|ではないでしょうか|のではないでしょうか|と考えられます|と思われます|かもしれません",
      "断定を避ける語尾が続くと、内容の責任が誰にもありません。",
      "根拠があるなら言い切ります。不確実なら範囲を示します。",
      min_count=1),

    R("ja-announcement", "block", ["ja"], "構成",
      r"について(?:説明|解説)します|を見ていきましょう|見てみましょう|解説します|紹介します|まとめます|以下で(?:説明|解説)|まず最初に|結論から言うと",
      "本題の前の宣言です。読者は内容を待たされます。",
      "宣言を削り、最初の事実から書きます。",
      min_count=1),

    R("ja-buzz", "warn", ["ja"], "語彙",
      r"ソリューション|シナジー|レバレッジ|アジャイル|イノベーション|トランスフォーメーション|エコシステム|ステークホルダー|コンセンサス|アラインメント|ガバナンス|コンプライアンス|カスタマーサクセス|ユーザー体験|顧客体験|ワンストップ|シームレス|最先端|革新的|圧倒的|持続可能|共創|DX|グロース",
      "カタカナ語や抽象語が、具体的な動作や結果を置き換えています。",
      "誰が何をしたか、何がどう変わったかに置き換えます。",
      min_count=1, max_per_1000=2.0),

    R("ja-empty-verb", "warn", ["ja"], "語彙",
      r"を実現します|を可能にします|を提供します|をサポートします|を実現する|を目指します|に取り組みます|を推進します|を強化します|を最適化します|を活用します|に貢献します",
      "動詞が抽象的なので、何をどうするのかが見えません。",
      "具体的な動作に置き換えます。「請求書をCSVで出力する」など。",
      min_count=1, max_per_1000=2.0),

    R("ja-nominalization", "warn", ["ja"], "構文",
      r"の実現|の推進|の強化|の最適化|の活用|の向上|の改善|の拡大|の創出|の構築|の提供",
      "動詞を名詞にすると、主語と責任が見えにくくなります。",
      "動詞に戻します。「実現のための推進」なら「〜する」と書きます。",
      min_count=1, max_per_1000=2.0),

    R("ja-polite-excess", "warn", ["ja"], "語用",
      r"させていただきます|させていただく|いただけますと幸いです|のほど|ございます|くださいませ|お願い申し上げます",
      "過剰な敬語が情報を薄めます。",
      "「します」「してください」で足ります。",
      min_count=1),

    R("ja-filler", "warn", ["ja"], "構文",
      r"において|に関して|にとって|に対して|によって|を通じて|に基づいて|を踏まえて|の一環として|をはじめ|などが挙げられます",
      "前置きの接続句が続くと、文の焦点がぼけます。",
      "削れるものは削り、必要な条件だけ残します。",
      min_count=1, max_per_1000=2.0),

    R("ja-grand", "warn", ["ja"], "語用",
      r"未来を創る|社会を変える|世界を変える|新しい時代|可能性を広げる|価値を創造|課題を解決|社会課題|持続可能な未来|明るい未来",
      "大げさな目的語が、実際の変更点を隠します。",
      "変更点、対象、数を書きます。",
      min_count=1),

    R("ja-chatbot", "block", ["ja"], "語用",
      r"いかがでしょうか|ぜひお試しください|お気軽にお問い合わせください|ご不明な点がございましたら|お役に立てれば幸いです",
      "チャットボットの語尾が成果物に残っています。",
      "削除し、内容で終わります。",
      min_count=1),

    R("ja-degree", "warn", ["ja"], "語彙",
      r"とても|非常に|極めて|大変",
      "程度副詞が並ぶと、基準のない強調になります。",
      "数値、比較、範囲に置き換えます。",
      min_count=3),

    R("ja-long-modifier", "warn", ["ja"], "構文",
      r"の[^。\n]{1,12}の[^。\n]{1,12}の",
      "「の」の連鎖で修飾語が重なり、主語が遠くなります。",
      "文を分けるか、修飾語を一つにします。",
      min_count=1),

    R("ja-fake-source", "warn", ["ja"], "事実",
      r"データによると|調査によると|研究によると|統計によると",
      "出典のないデータ表現です。",
      "機関、年、対象、URLを書きます。出せないなら数字を削ります。",
      min_count=1),

    R("ja-trend", "warn", ["ja"], "構成",
      r"近年|ますます|今後ますます|時代は|変化し続ける|目まぐるしく",
      "時代の傾向で内容を包むと、誰が何をしたかが見えません。",
      "具体的な時期、対象、変化を書きます。",
      min_count=1),

    R("ja-passive", "warn", ["ja"], "構文",
      r"されています|が行われています|が求められています|が期待されています",
      "受動態が続くと、行為者が消えます。",
      "行為者を戻すか、能動態にします。",
      min_count=2, max_per_1000=2.0),

    R("ja-translationese", "warn", ["ja"], "翻訳調",
      r"することができます|することが可能です|することが重要です|する必要があります|することが求められます",
      "英語の「can / it is important to」を直訳した形です。",
      "「できます」「重要です」と短く書きます。",
      min_count=1),

    R("ja-meeting", "block", ["ja"], "構成",
      r"本日は|以上です|まとめると|まず最初に|結論から言うと",
      "会議の口頭表現が文章に残っています。",
      "削除し、内容だけ残します。",
      min_count=1),

    R("ja-reassurance", "warn", ["ja"], "語用",
      r"ご安心ください|心配いりません|そのままお任せください|いつでも変更できます|自由に編集できます",
      "過剰な安心させ方は、読者を子ども扱いします。",
      "状態、変更点、確認方法を書きます。",
      min_count=1),

    R("ja-halfwidth-punct", "hint", ["ja"], "表記",
      r"[\u3040-\u30ff\u4e00-\u9fff][,;:!?]",
      "日本語の直後に半角の句読点が混ざっています。",
      "全角の、。！？に直します。",
      min_count=2, max_per_1000=3.0),

    R("ja-ellipsis", "hint", ["ja"], "表記",
      r"\.\.\.",
      "三点リーダーを半角ピリオドで書いています。",
      "……に直します。",
      min_count=1),
]

METRICS = {
    "sentence_cv_min": 0.35,
    "sentence_min_count": 12,
    "paragraph_cv_min": 0.35,
    "paragraph_min_count": 6,
    "list_ratio_max": 0.45,
    "list_min_lines": 12,
    "list_min_bullets": 8,
    "bold_per_1000_max": 6.0,
    "bold_min_count": 8,
    "transition_share_max": 0.25,
    "transition_min_sentences": 15,
    "colon_triad_max": 3,
}

PROCESS_MARKERS = (
    "探针", "快照", "证据", "门禁", "夹具", "哈希", "冒烟", "烟测",
    "基线", "dry-run", "验收矩阵", "可追溯备份", "最小改动",
    "回归矩阵", "发布门禁", "证据链",
)

PURPLE_MARKERS = (
    "不容置疑的", "长年薄茧", "太清醒", "清冷绝尘", "浮了毒", "旖旎",
    "伪饰", "四肢百骸", "对到让人绝望", "剥开迷雾", "雷霆般", "信徒",
    "神明", "灭顶", "侵略性", "宠溺", "稳稳接住", "彻底开悟",
    "逐字逐句", "压抑的真相", "太对了", "手术刀",
)


FICTION_EXCLUDE = {
    "zh-carrying-trait", "zh-carrying-trait-generic",
    "zh-correction-opener", "zh-zero-friction",
    "zh-stacked-modifiers-generic", "zh-unmotivated-negation",
}


# Fiction only. These rules are deliberately stricter than prose rules; they
# are enabled with `scan.py --fiction` so ordinary copy is not over-polished.
FICTION_RULES = [
    R("fic-not-but", "block", ["zh"], "小说-句式",
      r"(?:不是|并非)[^。！？\n]{1,30}(?:而是|，是)|[^。！？\n]{1,25}[，,]\s*(?:而)?不是[^。！？\n]{1,25}",
      "小说里用否定对仗制造深刻，读起来像解说，不像场景。",
      "写动作、感官、后果；让读者自己判断。",
      min_count=1),

    R("fic-even", "block", ["zh"], "小说-句式",
      r"连[^。！？\n]{1,20}都",
      "“连……都……”是用夸张代替具体反应，人物没有真正动起来。",
      "写身体反应或动作：手停住、呼吸乱了、汤洒了。",
      min_count=1),

    R("fic-compare-more", "block", ["zh"], "小说-句式",
      r"比[^。！？\n，,]{1,10}更",
      "比较级在叙述里是作者在打分，不是人物在经历。",
      "删掉比较，写两个具体状态。",
      min_count=1),

    R("fic-compare-still", "block", ["zh"], "小说-句式",
      r"比[^。！？\n，,]{1,10}还",
      "比较级加码会让描写滑向总结，读者离场景越来越远。",
      "写当下的感官，不写跨时间的比较。",
      min_count=1),

    R("fic-precise-paradox", "block", ["zh"], "小说-描写",
      r"(?:声音|力道|力气|动静|动作|脚步)(?:不大|不大不小|很轻)[^。！？\n]{0,20}(?:但|却|却让|刚好|恰好|正好)[^。！？\n]{0,20}(?:每个人|所有人|全场|所有人都|刚好|恰好|正好)",
      "“不大但所有人都……”是精准悖论：既想轻，又想有效果，结果是作者在解释效果。",
      "写一个能被看见或听见的细节，不写效果总结。",
      min_count=1),

    R("fic-single-char", "warn", ["zh"], "小说-描写",
      r"(?:走路|说话|声音|眼神|步伐|语气|呼吸)[^。！？\n]{0,4}[“\"]?(?:稳|直|沉|冷|狠|轻|慢|快)[”\"]?",
      "用一个字给整个人定性，是作者在贴标签，不是人物在动作。",
      "把那个字展开成一个动作或一个选择。",
      min_count=1),

    R("fic-panorama", "warn", ["zh"], "小说-描写",
      r"一时间[^。！？\n]{0,30}(?:剑影|刀光|人影|身影|火光|尘土|风声|杀气)[^。！？\n]{0,20}(?:纷飞|交错|四起|大作|翻飞|弥漫)",
      "上帝视角的全景描写，像在节省算力：给了气氛，没给任何人的具体动作。",
      "切到一个人物的眼睛和身体，写他看见什么、躲了什么。",
      min_count=1),

    R("fic-list-summary", "warn", ["zh"], "小说-描写",
      r"(?:[闹偷定比打杀救闯抢砸][^。！？\n]{1,8}[，,]){2,}",
      "把一场戏压成动词清单，读者看不到过程，只看到目录。",
      "选一个动作展开，其余留白。",
      min_count=1),

    R("fic-opening", "warn", ["zh"], "小说-结构",
      r"(?:^|\n)\s*(?:回到家|推开门|走进|醒来|睁开眼|下班|进门)[^。！？\n]{0,25}(?:香气|味道|阳光|风|声音|饭菜)[^。！？\n]{0,25}(?:钻入|扑面|涌来|照进|传来|飘来)",
      "开篇用“回家 + 气味/阳光钻进来”的起手式，场景还没建立，情绪先到位。",
      "从一个人正在做的事开始，让气味晚一点出现。",
      min_count=1),

    R("fic-closing", "warn", ["zh"], "小说-结构",
      r"(?:他知道|她知道|他明白|她明白|他终于|她终于|这就是)[^。！？\n]{0,30}(?:爱|家|温暖|幸福|意义|答案|成长|命运)",
      "结尾替读者总结意义，把留白填死了。",
      "停在一个动作或一个物件上，不要解释它代表什么。",
      min_count=1),

    R("fic-finger", "warn", ["zh"], "小说-人物",
      r"(?:指尖|指腹|手指)(?:触摸|触碰|抚过|握着|捏着|划过|摩挲)",
      "人手抓东西时不会只用指尖；这种写法是镜头替身体做决定。",
      "写整只手：抓住、攥紧、拎起、按住。",
      min_count=1),

    R("fic-emotion-whiplash", "warn", ["zh"], "小说-人物",
      r"(?:前一秒|上一秒|刚刚还)[^。！？\n]{0,25}(?:下一秒|下一刻|转眼|突然)[^。！？\n]{0,25}(?:哭|笑|怒|吼|摔|抱|亲|打|爆发|翻脸|争吵|剧情)",
      "人物情绪在两句之间翻转，没有触发事件；读者只看到作者需要剧情。",
      "补一个可见的触发，或者把情绪变化拉开。",
      min_count=1),

    R("fic-scene-jump", "warn", ["zh"], "小说-结构",
      r"(?:下一秒|下一刻|转眼间|话音刚落|就在这时)[^。！？\n]{0,30}(?:出现在|闯进|敲门|冲进|站在|坐在|拔剑|开枪|抱住)",
      "场景硬切，人物像被作者搬到下一个布景；中间没有过渡。",
      "补路程、时间或一个感官过渡；不需要就删掉硬切。",
      min_count=1),

    R("fic-out-of-scene", "warn", ["zh"], "小说-人物",
      r"(?:明明)?不在场[^。！？\n]{0,20}(?:却|竟然|居然)[^。！？\n]{0,20}(?:知道|说出|提到|点破)",
      "不在场的人知道现场细节，是全员上帝视角。",
      "让信息通过在场的人、物证或传言传递。",
      min_count=1),

    R("fic-vague", "warn", ["zh"], "小说-叙述",
      r"(?:仿佛|似乎|某种|不知为何|说不清|难以言说|无法形容|一种[^。！？\n]{0,8}的感觉)",
      "能说清的地方偏要说成谜语，读者被挡在信息外面。",
      "把“某种感觉”换成具体的感官或动作；留白留在事件之间，不留在句子内部。",
      min_count=1),

    R("fic-forced-turn", "warn", ["zh"], "小说-结构",
      r"(?:突然|忽然|竟然|没想到|就在这时)[^。！？\n]{0,25}(?:出现|闯进|敲门|冲进|转身|站起|拔剑|开枪|哭|笑|晕倒)",
      "用“突然”直接搬来新事件或新角色，冲突是有了，因果没有。",
      "删掉突然；如果事件必须发生，先埋一个可见的伏笔。",
      min_count=1, dedupe_with=["fic-scene-jump"]),

    R("fic-stock-imagery", "block", ["zh"], "小说-意象",
      r"命运(?:的)?齿轮|石子(?:的)?涟漪|无形(?:的)?大手|历史的车轮|时代的洪流|齿轮(?:开始)?转动|涟漪(?:般|一样)?(?:扩散|荡开)",
      "批发式意象：命运齿轮、石子涟漪、无形大手，都是现成氛围组，没有具身体验。",
      "换成一个只有这个人物会注意到的具体物件或动作。",
      min_count=1),

    R("fic-emotion-pile", "warn", ["zh"], "小说-情绪",
      r"颤抖|颤栗|战栗|窒息|嘶吼|咆哮|抽搐|痉挛|崩溃|撕裂",
      "强动词堆叠，情绪没有事件锚点；读者只看到修辞体操。",
      "删到只剩一个动作，把触发事件写出来。",
      min_count=3, max_per_1000=2.0),

    R("fic-self-deconstruction", "warn", ["zh"], "小说-结构",
      r"(?:看似|表面上|说到底|归根结底)[^。！？\n]{0,25}(?:其实|不过|只是|而是)|(?:我|这)(?:不是|并非)在[^。！？\n]{1,15}(?:而是|只是)",
      "结尾套娃式反转，用自我解构掩盖内容贫瘠；读者被绕了一圈，没得到新东西。",
      "删掉反转，停在事实或动作上；要反转就前面埋线。",
      min_count=1, dedupe_with=["fic-not-but"]),

    R("fic-pseudo-connection", "warn", ["zh"], "小说-句式",
      r"(?:仿佛|正如)[^。！？\n，,]{0,20}(?:命运|注定|宿命|轮回|因果|一切|所有|某种)",
      "用“仿佛/正如”硬连因果，句子看起来有哲理，实际没有逻辑。",
      "删掉连接词，写清两件事的实际关系；写不清就删。",
      min_count=2),

    R("fic-padding", "warn", ["zh"], "小说-篇幅",
      r"(?:极其|极为|无比)[^。！？\n]{0,8}(?:极其|极为|无比)|(?:非常|十分)[^。！？\n]{0,6}(?:非常|十分)",
      "用程度词拉长句子，内容密度没有增加。",
      "删到一个程度词，或者换成具体程度。",
      min_count=1),

    R("fic-long-sentence", "warn", ["zh"], "小说-篇幅",
      r"[^。！？\n]{100,}",
      "单句超过 100 字，读者要回头找主语；篇幅膨胀不等于丰富。",
      "拆成两到三句，一句一个动作。",
      min_count=1),

    R("fic-pov-jump", "warn", ["zh"], "小说-视角",
      r"(?:与此同时|同一时间|另一边|而在另一边|此时此刻)[^。！？\n]{0,25}(?:他|她|他们|她们|这|那)",
      "POV 硬跳：读者还在上一场的眼睛里，叙述突然搬到另一个地方。",
      "用空行或分节切换，或者先给当前 POV 一个离开的动作。",
      min_count=1),

    R("fic-backstory-dump", "warn", ["zh"], "小说-视角",
      r"(?:原来|曾经|多年前|从小|事实上|据说|资料(?:显示|里)|档案(?:里|显示))[^。！？\n]{0,30}",
      "场景中途插资料或前史，话题突变；读者被拉出当前视角。",
      "把前史放到场景外，或通过对话、物件、动作自然带出。",
      min_count=1),

    R("fic-resume", "warn", ["zh"], "小说-视角",
      r"(?:他是|她是|这个人|此人)(?:一(?:个|名|位))?[^。！？\n]{0,20}(?:公司|创始人|毕业|担任|擅长|来自|今年)[^。！？\n]{0,20}",
      "人物介绍写成简历：公司、学历、擅长；当前 POV 看不到这些。",
      "只写当前 POV 能观察到的东西：衣服、动作、口音、手上的茧。",
      min_count=1),

    R("fic-omniscient", "warn", ["zh"], "小说-视角",
      r"(?:所有人都不知道|没有人知道|没有人注意到|谁也没有想到|殊不知)[^。！？\n]{0,25}",
      "叙述者突然全知：读者只能跟着 POV，不能拿到场外信息。",
      "删掉全知句；让信息通过在场的人、物证或对话出现。",
      min_count=1),

    R("fic-pov-internal", "warn", ["zh"], "小说-视角",
      r"(?:他|她)(?:知道|明白|意识到)[^。！？\n]{0,10}(?:她|他)(?:在|想|爱|恨|害怕|难过|决定)",
      "直接写另一个人的内心；当前 POV 只能看见表情、动作、语气。",
      "改成可观察的细节：她没抬头、手指捏紧车票、声音低下去。",
      min_count=1),

    R("fic-collocation", "warn", ["zh"], "小说-语言",
      r"颤抖的(?:体温|温度|光线|空气|时间|沉默)|混乱(?:而|又|却)?有序|有序(?:而|又|却)?混乱|冰冷的(?:火焰|热情)|燃烧的(?:冰|雪)|沉默的(?:尖叫|呐喊)",
      "名词和形容词/动词搭配不上，或者两个修饰语互相矛盾；读者会停下来算这句话什么意思。",
      "先问主语能不能做这个动作，再问两个修饰语是否打架；删掉一个，或换成具体动作。",
      min_count=1),

    R("fic-favorite-word", "warn", ["zh"], "小说-语言",
      r"黏腻|滞重|手术刀(?:般|似|一样)",
      "作者偏爱的高权重词，放在不搭的气质里；出现一次是风格，反复出现是口头禅。",
      "换成一个当前人物会注意到的具体细节；保留时确认它真的属于这个场景。",
      min_count=1),

    R("fic-stock-description", "warn", ["zh"], "小说-语言",
      r"鲨鱼夹|几缕碎发|碎发垂在|发丝垂在|头发挽在脑后",
      "固定人物描写模板：每个女性都鲨鱼夹、几缕碎发；人类作者会按人物换细节。",
      "按这个人物的职业、年龄、当天状态换一个细节；不要复用同一套。",
      min_count=1),

    R("fic-adjective-pile", "warn", ["zh"], "小说-语言",
      r"(?:[^\s，。！？]{1,4}的){3,}",
      "形容词堆在名词前，读者要拆半天；多数修饰删掉后信息不变。",
      "留一个最具体的修饰，其余改成动作或感官。",
      min_count=1),

    R("fic-degree-pile", "warn", ["zh"], "小说-语言",
      r"极其|非常|十分|格外|异常|无比|越发|愈发",
      "程度副词堆叠，情绪没有具体幅度；副词在替形容词加班。",
      "删到零到一个，或者换成具体程度。",
      min_count=3),

    R("fic-stock-simile", "block", ["zh"], "小说-语言",
      r"(?:如同一|宛如|就像|仿佛)(?:一)?(?:颗|块|道|片)[^。！？\n]{1,15}(?:砸进|投进|落入|坠入|掉进)[^。！？\n]{1,15}(?:里|中)",
      "现成比喻框架：如同一颗……砸进……里；删掉涟漪，框架还在。",
      "删掉比喻，写这个动作对人物或场景的实际影响。",
      min_count=1),
]
