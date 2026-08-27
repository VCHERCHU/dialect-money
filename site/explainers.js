/*
 * Data only. The app in index.html renders whatever LIBRARY contains and reads
 * no explainer by name — adding one is a pure data change.
 *
 * PROTOTYPE NOTES
 * - `source.url` points at the source's home page. Deep links land here until a
 *   real crawler resolves them; a fabricated deep link is worse than an honest
 *   home page. `source.page` names the page the script came from.
 * - `script` is written Chinese, shared across all three dialects. Written
 *   dialect is not standardised in Singapore — only the *narration* differs.
 *   This is a real product constraint, not a shortcut.
 * - Scripts are drafts. Nothing here has been through the human check the
 *   problem statement requires, and no specific figure or rate is quoted.
 * - `keywords` drives retrieval in ask.html. Terms are multi-character on
 *   purpose: a single common character matches nearly every question and would
 *   make every explainer look relevant. A real assistant would replace this
 *   scoring with embeddings, but not the contract around it -- answer only from
 *   what was retrieved, cite it, refuse otherwise.
 */

window.LIBRARY = {

  /* Narration languages offered. ttsLang is the browser voice used as a
     stand-in — see the placeholder-voice notice in the app. There is no real
     Hokkien or Teochew TTS behind this yet; that is assumption 2. */
  dialects: [
    { id: 'hokkien',   zh: '福建话', en: 'Hokkien',   ttsLang: 'zh-CN' },
    { id: 'teochew',   zh: '潮州话', en: 'Teochew',   ttsLang: 'zh-CN' },
    { id: 'cantonese', zh: '广东话', en: 'Cantonese', ttsLang: 'zh-HK' }
  ],

  /* The whitelist. The crawler reads these and nothing else. */
  whitelist: [
    { name: 'MoneySense', url: 'https://www.moneysense.gov.sg' },
    { name: 'CPF',        url: 'https://www.cpf.gov.sg' },
    { name: 'MAS',        url: 'https://www.mas.gov.sg' },
    { name: 'MAS FID',    url: 'https://eservices.mas.gov.sg/fid/institution/print' },
    { name: 'IRAS',       url: 'https://www.iras.gov.sg' },
    { name: 'MOF',        url: 'https://www.mof.gov.sg' },
    { name: 'gov.sg',     url: 'https://www.gov.sg' }
  ],

  /* ---------------------------------------------------------------
     WHO IS SELLING, not what is being sold.

     v1 explains and does not advise, so nothing here may say whether
     a product is worth buying. But there is one fact about any offer
     that IS authoritative, checkable, and free of judgement: whether
     the institution behind it is licensed by MAS at all. The MAS
     Financial Institutions Directory is the single reference for that,
     and it is the only source in the whitelist that speaks about
     specific commercial firms.

     Rule for every explainer and every narration: when an institution
     or a representative is referred to, it is referred to through the
     FID and nowhere else. No other list, no company website, no
     recollection. If a firm is not in the FID, the honest answer is
     "not found here" — never an implied verdict either way.
     --------------------------------------------------------------- */
  verify: {
    zh:  '还有一件事，先查清楚：卖给你的这家公司，在MAS的名册里面吗？',
    ask: '你公司的名字，让我在MAS的名册里查一查，可以吗？',
    labelZh: '查一查这家公司',
    labelEn: 'Check the firm — MAS Financial Institutions Directory',
    url: 'https://eservices.mas.gov.sg/fid/institution/print'
  },

  lastCrawl: '2026-08-26',

  explainers: [
    {
      id: 'ip-rider',
      keywords: ['附加险', '附加合约', 'rider', '住院', '看病', '医院', '自己付', '自付', '共付', 'shield', '医疗保险', '保费会涨'],
      titleZh: '加了附加险，看病真的不用自己付钱？',
      titleEn: 'Integrated Shield riders — what "no cash outlay" leaves out',
      seconds: 95,
      published: '2026-08-26',
      source: { name: 'MoneySense', page: 'Integrated Shield Plans and riders', url: 'https://www.moneysense.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'ready', cantonese: 'ready' },
      script: [
        '保险公司说，加了这个附加险，看病你就不用自己出钱。',
        '听起来很好。但是附加险不是免费的，你每年要多付保费。',
        '而且，你现在的保费不等于以后的保费。年纪越大，保费会调高。',
        '还有一点：如果看病都不用自己付，有些人会更常去看医生，整体的保费就跟着涨。',
        '这不是说附加险不好。是说你要知道你在买什么。'
      ],
      ask: [
        '这个附加险，我七十五岁、八十岁的时候，保费大概是多少？',
        '如果以后我付不起，可以只取消附加险，保住主要的保险吗？',
        '看病的时候，我自己最多要付多少？'
      ]
    },
    {
      id: 'guaranteed-or-not',
      keywords: ['保证', '不保证', '估计', 'illustration', '到期', '拿回', '分红', '回报', '预估', '保单上的数字'],
      titleZh: '保单上的大数目，是保证的还是估计的？',
      titleEn: 'Guaranteed vs non-guaranteed figures on a benefit illustration',
      seconds: 80,
      published: '2026-08-26',
      source: { name: 'MoneySense', page: 'Understanding your policy illustration', url: 'https://www.moneysense.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'ready', cantonese: 'ready' },
      script: [
        '保单上的数字，分两种：保证的，和不保证的。',
        '保证的，公司一定要给你。不保证的，是估计，可能多，也可能少。',
        '销售员指给你看的那个大数目，很多时候是不保证的那一栏。',
        '所以你要问一句：如果不保证的部分完全没有，我拿回多少？'
      ],
      ask: [
        '哪些数字是保证的？请你指给我看。',
        '如果不保证的部分是零，我到期拿回多少？',
        '我提早取消，会亏多少钱？'
      ]
    },
    {
      id: 'fd-promo-rate',
      keywords: ['定期存款', '存款', '利息', '利率', '促销', '年利率', 'fixed deposit', '银行利息', '提早拿', '锁'],
      titleZh: '定期存款的高利息，为什么拿到手好像变少了？',
      titleEn: 'Fixed deposit promo rates — per annum, lock-in, and the drop-back',
      seconds: 85,
      published: '2026-08-19',
      source: { name: 'MoneySense', page: 'Deposits and interest rates', url: 'https://www.moneysense.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'queued', cantonese: 'ready' },
      script: [
        '银行贴出来：利息比平时高很多。',
        '第一件事：那个是一年的利息。你存三个月，拿到的是四分之一。',
        '第二件事：钱锁在里面。提早拿出来，利息可能就没有了。',
        '第三件事：促销利息通常只算第一段时间，之后会掉回去。',
        '定期存款本身是安全的。要看清楚的，是时间。'
      ],
      ask: [
        '这个利息算几个月？到期以后变成多少？',
        '我提早拿钱出来，要罚多少？',
        '最低要存多少钱才有这个利息？'
      ]
    },
    {
      id: 'free-gift',
      keywords: ['礼物', '赠品', '超市券', '电饭锅', '旅行', '签名就送', 'gift', '免费送'],
      titleZh: '签名就送礼物，礼物的钱是谁出的？',
      titleEn: 'Sign-up gifts — who actually pays for the rice cooker',
      seconds: 70,
      published: '2026-08-19',
      source: { name: 'MoneySense', page: 'Before you buy a financial product', url: 'https://www.moneysense.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'ready', cantonese: 'ready' },
      script: [
        '签名就送超市券、送电饭锅、送旅行。',
        '礼物是真的，你会拿到。',
        '不过礼物的钱，是从你付的保费里面出来的。',
        '一份保单你可能要付十年、二十年；礼物值几十块。',
        '所以顺序是：先问清楚保单，礼物最后才算。'
      ],
      ask: [
        '如果我不要礼物，保费可以便宜一点吗？',
        '这份保单我要付多少年？一共多少钱？',
        '我可以带资料回家看几天再决定吗？'
      ]
    },
    {
      id: 'whole-life-vs-term',
      keywords: ['终身', '定期保险', '人寿', '寿险', 'term', 'whole life', '储蓄', '保额', '哪一种好'],
      titleZh: '终身保险和定期保险，差在哪里？',
      titleEn: 'Whole life vs term — what the extra premium is buying',
      seconds: 90,
      published: '2026-08-12',
      source: { name: 'MoneySense', page: 'Types of life insurance', url: 'https://www.moneysense.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'ready', cantonese: 'queued' },
      script: [
        '两种保险。终身的，保到你走；定期的，保二十年或三十年。',
        '同样的保额，定期的保费便宜很多。',
        '终身的贵，是因为里面有一部分当存钱用，而那部分的回报不一定高。',
        '哪一种好？看你要保的是什么，你几岁，家里还有谁靠你。'
      ],
      ask: [
        '同样的保额，定期保险的保费是多少？请你算给我看。',
        '这份保单里，多少是保障，多少是储蓄？',
        '我这个年纪，还需要新的人寿保险吗？'
      ]
    },
    {
      id: 'how-the-adviser-is-paid',
      keywords: ['佣金', '销售员', '代理', 'agent', 'commission', '赚多少', '顾问', '为什么推荐'],
      titleZh: '销售员卖这份保单，他赚多少？',
      titleEn: 'How the person selling to you is paid — and why you may ask',
      seconds: 65,
      published: '2026-08-12',
      source: { name: 'MAS', page: 'Financial adviser representatives', url: 'https://www.mas.gov.sg' },
      audio: { hokkien: 'ready', teochew: 'ready', cantonese: 'ready' },
      script: [
        '销售员帮你买保险，他会拿佣金。这是正常的，不是骗人。',
        '不过不同的产品，佣金不一样。佣金高的，他可能会先介绍给你。',
        '你可以直接问他。这是你的权利，问了不失礼。'
      ],
      ask: [
        '你卖这份保单，佣金大概多少？',
        '还有没有更便宜的选择？为什么你推荐这一个？',
        '你是代表一家公司，还是很多家？'
      ]
    }
  ]
};
