/*
 * Data only. The app in index.html renders whatever LIBRARY contains and reads
 * no explainer by name — adding one is a pure data change.
 *
 * PROTOTYPE NOTES
 * - `source.url` points at the source's home page. Deep links land here until a
 *   real crawler resolves them; a fabricated deep link is worse than an honest
 *   home page. `source.page` names the page the script came from.
 * - `script` is written Chinese. It stays the shared text for Teochew and
 *   Cantonese: written dialect is not standardised in Singapore, so for those
 *   two only the *narration* differs. That is a real product constraint.
 * - Hokkien is now the exception. `hokkien.script` carries colloquial Hokkien
 *   (白話) in Han characters — the register a person actually speaks, not a
 *   literary reading of Mandarin. This is what pipeline/tts.py feeds to
 *   MERaLiON, and feeding it Mandarin instead produces 讀書音: correct Hokkien
 *   phonology wrapped around Mandarin vocabulary, which sounds like a
 *   broadcast rather than a person. The Mandarin `script` stays alongside it
 *   as the checkpoint a literate reviewer can actually read.
 * - `hokkien.tailo` is line-for-line with `hokkien.script`, for a human reader
 *   or reviewer. `hokkien.checked` records whether a native Singapore Hokkien
 *   speaker has reviewed it. It is false everywhere, and the app says so.
 * - Scripts are drafts. Nothing here has been through the human check the
 *   problem statement requires, and no specific figure or rate is quoted.
 * - `keywords` drives retrieval in ask.html. Terms are multi-character on
 *   purpose: a single common character matches nearly every question and would
 *   make every explainer look relevant. A real assistant would replace this
 *   scoring with embeddings, but not the contract around it -- answer only from
 *   what was retrieved, cite it, refuse otherwise.
 */

window.LIBRARY = {

  /* Narration languages offered.

     `narration: 'meralion'` means pre-rendered audio exists under site/audio/,
     produced by scripts/render_site_audio.py from `hokkien.script`. The app
     plays those files and falls back to the browser voice if one is missing.

     `narration: 'placeholder'` means there is no real voice for this dialect
     yet — `ttsLang` names the browser voice used as a stand-in so the shape of
     the experience can be judged. That is assumption 2, still untested. */
  dialects: [
    { id: 'hokkien',   zh: '福建话', en: 'Hokkien',   ttsLang: 'zh-CN', narration: 'meralion'    },
    { id: 'teochew',   zh: '潮州话', en: 'Teochew',   ttsLang: 'zh-CN', narration: 'placeholder' },
    { id: 'cantonese', zh: '广东话', en: 'Cantonese', ttsLang: 'zh-HK', narration: 'placeholder' }
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

    /* The Hokkien form of the same two lines. Without this the closing line —
       the one line every explainer ends on — would drop back to Mandarin
       mid-narration. Its clip is rendered once as audio/verify.hokkien.mp3
       and shared by every explainer, since the line never varies. */
    hokkien: {
      script: '猶有一件事，先查予清楚：賣予你的這間公司，佇MAS的名冊內底無？',
      tailo:  'Iáu ū tsi̍t kiānn sū, sing tshâ hōo tshing-tshó: bē hōo lí ê tsit king kong-si, tī MAS ê miâ-tsheh lāi-té bô?',
      ask:    '你公司的名，予我佇MAS的名冊查一下，會使無？',
      checked: false
    },
    labelZh: '查一查这家公司',
    labelEn: 'Check the firm — MAS Financial Institutions Directory',
    url: 'https://eservices.mas.gov.sg/fid/institution/print'
  },

  /* ---------------------------------------------------------------
     ART — one drawn situation per explainer.

     This is what a viewer who cannot read uses instead of a title:
     a man holding out a paper, a gift with a price tag, a coin stack
     beside a clock. Every consumer draws it inside
     <svg viewBox="0 0 120 80">, so the strings hold shapes only.

     It lives here rather than in a page because all three pages need
     it now. ask.html's own note says two pages is the point at which
     duplication is still cheaper than a build and "a third would
     change the answer" — this is the third.

     Palette is fixed to the dark stage: mint #6fd3ad for her and for
     the thing being explained, grey #a8a397 for whoever is selling,
     amber #f0b46a for the catch, paper #fbf9f4 for documents. An
     explainer with no entry falls back to 'ip-rider', which is the
     wedge for all of them anyway.
     --------------------------------------------------------------- */
  art: {
    'ip-rider':
      '<circle cx="24" cy="24" r="10" fill="#a8a397"/>' +
      '<rect x="12" y="38" width="24" height="34" rx="11" fill="#a8a397"/>' +
      '<rect x="44" y="22" width="32" height="42" rx="3" fill="#fbf9f4"/>' +
      '<rect x="49" y="30" width="22" height="3" rx="1.5" fill="#14140f"/>' +
      '<rect x="49" y="38" width="22" height="3" rx="1.5" fill="#14140f"/>' +
      '<rect x="49" y="46" width="13" height="3" rx="1.5" fill="#14140f"/>' +
      '<circle cx="96" cy="23" r="11" fill="#6fd3ad"/>' +
      '<rect x="82" y="39" width="28" height="33" rx="12" fill="#6fd3ad"/>',

    'guaranteed-or-not':
      '<rect x="20" y="16" width="34" height="52" rx="4" fill="#6fd3ad"/>' +
      '<rect x="66" y="16" width="34" height="52" rx="4" fill="none" stroke="#f0b46a" stroke-width="3" stroke-dasharray="7 6"/>' +
      '<rect x="27" y="30" width="20" height="4" rx="2" fill="#14140f"/>' +
      '<rect x="27" y="42" width="14" height="4" rx="2" fill="#14140f"/>',

    'fd-promo-rate':
      '<ellipse cx="42" cy="60" rx="26" ry="8" fill="#6fd3ad"/>' +
      '<ellipse cx="42" cy="50" rx="26" ry="8" fill="#6fd3ad"/>' +
      '<ellipse cx="42" cy="40" rx="26" ry="8" fill="#fbf9f4"/>' +
      '<circle cx="88" cy="30" r="18" fill="none" stroke="#f0b46a" stroke-width="3.4"/>' +
      '<path d="M88 20 L88 30 L96 34" stroke="#f0b46a" stroke-width="3.4" stroke-linecap="round" fill="none"/>',

    'free-gift':
      '<rect x="26" y="32" width="48" height="36" rx="4" fill="#6fd3ad"/>' +
      '<rect x="26" y="22" width="48" height="12" rx="4" fill="#fbf9f4"/>' +
      '<rect x="45" y="22" width="10" height="46" fill="#14140f"/>' +
      '<path d="M84 30 L102 30 L106 44 L88 50 Z" fill="#f0b46a"/>' +
      '<circle cx="90" cy="35" r="2.6" fill="#14140f"/>',

    'whole-life-vs-term':
      '<path d="M8 44 a26 26 0 0 1 52 0 Z" fill="#6fd3ad"/>' +
      '<path d="M34 44 L34 68" stroke="#6fd3ad" stroke-width="4" stroke-linecap="round"/>' +
      '<path d="M64 44 a24 24 0 0 1 48 0 Z" fill="none" stroke="#f0b46a" stroke-width="3.2" stroke-dasharray="8 6"/>' +
      '<path d="M88 44 L88 66" stroke="#f0b46a" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="6 5"/>',

    'how-the-adviser-is-paid':
      '<circle cx="46" cy="24" r="12" fill="#a8a397"/>' +
      '<rect x="30" y="42" width="32" height="30" rx="12" fill="#a8a397"/>' +
      '<circle cx="86" cy="46" r="15" fill="#f0b46a"/>' +
      '<circle cx="86" cy="46" r="8" fill="none" stroke="#14140f" stroke-width="2.6"/>' +
      '<path d="M62 50 L72 47" stroke="#a8a397" stroke-width="6" stroke-linecap="round"/>'
  },

  /* ---------------------------------------------------------------
     SYM / BEATS — a picture per LINE, not per explainer.

     `art` above answers "what is this explainer about" on a card or a
     title screen. This answers "what is being said right now", so a
     viewer who reads nothing still follows the argument: someone is
     selling you this, you pay every year, the payment rises with age,
     more claims push it up again, so know what you are buying.

     BEATS[id] is line-for-line with script (and with hokkien.script,
     which is the same length by construction). The appended MAS line
     has no entry and uses SYM.shield.
     --------------------------------------------------------------- */
  sym: {
    'sell':
      '<circle cx="24" cy="24" r="10" fill="#a8a397"/><rect x="12" y="38" width="24" height="34" rx="11" fill="#a8a397"/><rect x="44" y="22" width="32" height="42" rx="3" fill="#fbf9f4"/><rect x="49" y="30" width="22" height="3" rx="1.5" fill="#14140f"/><rect x="49" y="38" width="22" height="3" rx="1.5" fill="#14140f"/><rect x="49" y="46" width="13" height="3" rx="1.5" fill="#14140f"/><circle cx="96" cy="23" r="11" fill="#6fd3ad"/><rect x="82" y="39" width="28" height="33" rx="12" fill="#6fd3ad"/>',
    'coin-out':
      '<circle cx="38" cy="40" r="19" fill="#f0b46a"/><circle cx="38" cy="40" r="10" fill="none" stroke="#14140f" stroke-width="3.2"/><path d="M66 40 L102 40" stroke="#fbf9f4" stroke-width="4.5" stroke-linecap="round"/><path d="M91 30 L102 40 L91 50" stroke="#fbf9f4" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'coin-up':
      '<circle cx="30" cy="50" r="16" fill="#f0b46a"/><circle cx="30" cy="50" r="8" fill="none" stroke="#14140f" stroke-width="3"/><path d="M62 62 L62 24" stroke="#f0b46a" stroke-width="5" stroke-linecap="round"/><path d="M52 34 L62 24 L72 34" stroke="#f0b46a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><rect x="86" y="18" width="14" height="46" rx="3" fill="#6fd3ad"/>',
    'crowd':
      '<circle cx="20" cy="30" r="8" fill="#a8a397"/><rect x="10" y="42" width="20" height="26" rx="9" fill="#a8a397"/><circle cx="46" cy="26" r="9" fill="#a8a397"/><rect x="35" y="39" width="22" height="29" rx="10" fill="#a8a397"/><circle cx="74" cy="30" r="8" fill="#a8a397"/><rect x="64" y="42" width="20" height="26" rx="9" fill="#a8a397"/><circle cx="100" cy="26" r="9" fill="#f0b46a"/><rect x="89" y="39" width="22" height="29" rx="10" fill="#f0b46a"/>',
    'think':
      '<circle cx="28" cy="32" r="13" fill="#6fd3ad"/><rect x="12" y="50" width="32" height="24" rx="12" fill="#6fd3ad"/><path d="M58 8 L108 8 a5 5 0 0 1 5 5 L113 36 a5 5 0 0 1 -5 5 L72 41 L62 50 L64 41 L58 41 a5 5 0 0 1 -5 -5 L53 13 a5 5 0 0 1 5 -5 Z" fill="#fbf9f4"/><path d="M78 19 a5.4 5.4 0 1 1 5.4 5.4 L83.4 28" stroke="#14140f" stroke-width="3.2" stroke-linecap="round" fill="none"/><circle cx="83.4" cy="33" r="2.1" fill="#14140f"/>',
    'two-cols':
      '<rect x="20" y="16" width="34" height="52" rx="4" fill="#6fd3ad"/><rect x="66" y="16" width="34" height="52" rx="4" fill="none" stroke="#f0b46a" stroke-width="3" stroke-dasharray="7 6"/><rect x="27" y="30" width="20" height="4" rx="2" fill="#14140f"/><rect x="27" y="42" width="14" height="4" rx="2" fill="#14140f"/>',
    'estimate':
      '<circle cx="40" cy="40" r="19" fill="none" stroke="#f0b46a" stroke-width="3.6" stroke-dasharray="8 6"/><path d="M78 22 L78 58" stroke="#a8a397" stroke-width="3.6" stroke-linecap="round"/><path d="M69 31 L78 22 L87 31" stroke="#a8a397" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M69 49 L78 58 L87 49" stroke="#a8a397" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'ask':
      '<circle cx="20" cy="24" r="11" fill="#6fd3ad"/><rect x="7" y="38" width="26" height="30" rx="11" fill="#6fd3ad"/><path d="M42 10 L86 10 a5 5 0 0 1 5 5 L91 34 a5 5 0 0 1 -5 5 L56 39 L46 48 L48 39 L42 39 a5 5 0 0 1 -5 -5 L37 15 a5 5 0 0 1 5 -5 Z" fill="#fbf9f4"/><path d="M60 19 a4.8 4.8 0 1 1 4.8 4.8 L64.8 27" stroke="#14140f" stroke-width="2.9" stroke-linecap="round" fill="none"/><circle cx="64.8" cy="32" r="1.9" fill="#14140f"/><path d="M98 26 L110 26 M105.5 21 L110 26 L105.5 31" stroke="#a8a397" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="112" cy="52" r="9" fill="#a8a397"/>',
    'poster-rate':
      '<rect x="22" y="12" width="76" height="46" rx="4" fill="#fbf9f4"/><rect x="56" y="58" width="8" height="18" fill="#a8a397"/><path d="M38 48 L38 28" stroke="#f0b46a" stroke-width="5" stroke-linecap="round"/><path d="M31 35 L38 28 L45 35" stroke="#f0b46a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><circle cx="64" cy="28" r="5" fill="none" stroke="#14140f" stroke-width="3"/><circle cx="82" cy="44" r="5" fill="none" stroke="#14140f" stroke-width="3"/><path d="M60 48 L86 24" stroke="#14140f" stroke-width="3" stroke-linecap="round"/>',
    'clock':
      '<circle cx="60" cy="40" r="26" fill="none" stroke="#6fd3ad" stroke-width="5"/><path d="M60 22 L60 40 L74 48" stroke="#6fd3ad" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M96 18 L104 10 M96 62 L104 70" stroke="#f0b46a" stroke-width="4" stroke-linecap="round"/>',
    'lock':
      '<circle cx="36" cy="46" r="17" fill="#f0b46a"/><circle cx="36" cy="46" r="9" fill="none" stroke="#14140f" stroke-width="3"/><rect x="70" y="38" width="36" height="28" rx="5" fill="#6fd3ad"/><path d="M77 38 L77 27 a11 11 0 0 1 22 0 L99 38" stroke="#6fd3ad" stroke-width="4.6" fill="none"/><circle cx="88" cy="52" r="4.2" fill="#14140f"/>',
    'percent-drop':
      '<path d="M14 22 L44 22 L44 38 L74 38 L74 54 L100 54" stroke="#f0b46a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/><path d="M91 45 L100 54 L91 63" stroke="#f0b46a" stroke-width="5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'gift':
      '<rect x="30" y="32" width="52" height="38" rx="4" fill="#6fd3ad"/><rect x="30" y="21" width="52" height="13" rx="4" fill="#fbf9f4"/><rect x="50" y="21" width="11" height="49" fill="#14140f"/>',
    'gift-ok':
      '<rect x="22" y="32" width="50" height="38" rx="4" fill="#6fd3ad"/><rect x="22" y="21" width="50" height="13" rx="4" fill="#fbf9f4"/><rect x="41" y="21" width="11" height="49" fill="#14140f"/><path d="M84 44 L94 54 L110 34" stroke="#f0b46a" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'gift-price':
      '<rect x="24" y="32" width="48" height="36" rx="4" fill="#6fd3ad"/><rect x="24" y="21" width="48" height="13" rx="4" fill="#fbf9f4"/><rect x="43" y="21" width="10" height="47" fill="#14140f"/><path d="M82 28 L104 28 L108 44 L86 50 Z" fill="#f0b46a"/><circle cx="89" cy="34" r="2.8" fill="#14140f"/>',
    'years':
      '<rect x="12" y="28" width="16" height="32" rx="2.5" fill="#6fd3ad"/><rect x="32" y="28" width="16" height="32" rx="2.5" fill="#6fd3ad"/><rect x="52" y="28" width="16" height="32" rx="2.5" fill="#6fd3ad"/><rect x="72" y="28" width="16" height="32" rx="2.5" fill="#6fd3ad"/><path d="M98 40 L112 40 L114 52 L100 56 Z" fill="#f0b46a"/>',
    'umbrellas':
      '<path d="M8 44 a26 26 0 0 1 52 0 Z" fill="#6fd3ad"/><path d="M34 44 L34 68" stroke="#6fd3ad" stroke-width="4" stroke-linecap="round"/><path d="M64 44 a24 24 0 0 1 48 0 Z" fill="none" stroke="#f0b46a" stroke-width="3.2" stroke-dasharray="8 6"/><path d="M88 44 L88 66" stroke="#f0b46a" stroke-width="3.2" stroke-linecap="round" stroke-dasharray="6 5"/>',
    'coin-compare':
      '<circle cx="36" cy="40" r="23" fill="#f0b46a"/><circle cx="36" cy="40" r="12" fill="none" stroke="#14140f" stroke-width="3.4"/><circle cx="92" cy="48" r="13" fill="#6fd3ad"/><circle cx="92" cy="48" r="6.5" fill="none" stroke="#14140f" stroke-width="2.8"/>',
    'coin-save':
      '<rect x="22" y="34" width="48" height="34" rx="6" fill="#6fd3ad"/><rect x="37" y="26" width="18" height="9" rx="3.5" fill="#fbf9f4"/><circle cx="46" cy="52" r="9" fill="#f0b46a"/><path d="M90 58 L90 32" stroke="#a8a397" stroke-width="4" stroke-linecap="round" stroke-dasharray="7 5"/><path d="M82 39 L90 31 L98 39" stroke="#a8a397" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'commission':
      '<circle cx="44" cy="24" r="12" fill="#a8a397"/><rect x="28" y="42" width="32" height="30" rx="12" fill="#a8a397"/><circle cx="88" cy="46" r="15" fill="#f0b46a"/><circle cx="88" cy="46" r="8" fill="none" stroke="#14140f" stroke-width="2.6"/><path d="M62 50 L74 47" stroke="#a8a397" stroke-width="6" stroke-linecap="round"/>',
    'commission-high':
      '<circle cx="30" cy="28" r="12" fill="#a8a397"/><rect x="14" y="45" width="32" height="27" rx="12" fill="#a8a397"/><circle cx="70" cy="56" r="11" fill="#f0b46a"/><circle cx="96" cy="42" r="15" fill="#f0b46a"/><path d="M58 28 L58 12" stroke="#f0b46a" stroke-width="4" stroke-linecap="round"/><path d="M51 19 L58 12 L65 19" stroke="#f0b46a" stroke-width="4" stroke-linecap="round" stroke-linejoin="round" fill="none"/>',
    'shield':
      '<path d="M60 8 L96 22 L96 42 c0 18 -15 30 -36 34 c-21 -4 -36 -16 -36 -34 L24 22 Z" fill="none" stroke="#f0b46a" stroke-width="5"/><circle cx="54" cy="38" r="13" fill="none" stroke="#f0b46a" stroke-width="5"/><path d="M64 48 L76 60" stroke="#f0b46a" stroke-width="5" stroke-linecap="round"/>'
  },

  beats: {
    'ip-rider': ['sell', 'coin-out', 'coin-up', 'crowd', 'think'],
    'guaranteed-or-not': ['two-cols', 'estimate', 'sell', 'ask'],
    'fd-promo-rate': ['poster-rate', 'clock', 'lock', 'percent-drop', 'think'],
    'free-gift': ['gift', 'gift-ok', 'gift-price', 'years', 'ask'],
    'whole-life-vs-term': ['umbrellas', 'coin-compare', 'coin-save', 'think'],
    'how-the-adviser-is-paid': ['commission', 'commission-high', 'ask']
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
      hokkien: {
        checked: false,
        title: '加了附加險，看病真正免家己納錢？',
        script: [
          '保險公司講，加這个附加險，看病你就免家己出錢。',
          '聽起來真好。毋過附加險毋是免費的，你每年愛加納保費。',
          '而且，你這馬的保費毋等於以後的保費。年歲愈大，保費會起。',
          '猶有一點：若是看病都免家己納，有的人會較常去看醫生，全部的保費就跟著起。',
          '這毋是講附加險無好。是講你愛知影你在買啥物。'
        ],
        tailo: [
          'Pó-hiám kong-si kóng, ka tsit ê hù-ka-hiám, khuànn-pēnn lí tō bián ka-kī tshut-tsînn.',
          'Thiann-khí-lâi tsin hó. M̄-koh hù-ka-hiám m̄ sī bián-huì ê, lí muí nî ài ke la̍p pó-huì.',
          'Jî-tshiánn, lí tsit-má ê pó-huì m̄ tíng-î í-āu ê pó-huì. Nî-huè jú tuā, pó-huì ē khí.',
          'Iáu ū tsi̍t tiám: nā-sī khuànn-pēnn to bián ka-kī la̍p, ū ê lâng ē khah tshiâng khì khuànn i-sing, tsuân-pōo ê pó-huì tō kin-tuè khí.',
          'Tse m̄ sī kóng hù-ka-hiám bô hó. Sī kóng lí ài tsai-iánn lí tī bé siánn-mih.'
        ],
        ask: [
          '這个附加險，我七十五歲、八十歲的時陣，保費大概偌濟？',
          '若是以後我納無起，會使干焦取消附加險，保住主要的保險無？',
          '看病的時陣，我家己最多愛納偌濟？'
        ]
      },
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
      hokkien: {
        checked: false,
        title: '保單頂的大數字，是有保證的抑是臆的？',
        script: [
          '保單頂的數字，分兩款：有保證的，佮無保證的。',
          '有保證的，公司一定愛予你。無保證的，是臆的，可能較濟，嘛可能較少。',
          '賣保險的指予你看的彼个大數字，真多時是無保證的彼欄。',
          '所以你愛問一句：若是無保證的部份完全無，我提倒轉偌濟？'
        ],
        tailo: [
          'Pó-tuann tíng ê sòo-jī, hun nn̄g khuán: ū pó-tsìng ê, kah bô pó-tsìng ê.',
          'Ū pó-tsìng ê, kong-si it-tīng ài hōo lí. Bô pó-tsìng ê, sī ioh ê, khó-lîng khah tsē, mā khó-lîng khah tsió.',
          'Bē pó-hiám ê kí hōo lí khuànn ê hit ê tuā sòo-jī, tsin tsē sî sī bô pó-tsìng ê hit nuâ.',
          'Sóo-í lí ài mn̄g tsi̍t kù: nā-sī bô pó-tsìng ê pōo-hūn uân-tsuân bô, guá the̍h tò-tńg lō-tsē?'
        ],
        ask: [
          '佗一寡數字是有保證的？請你指予我看。',
          '若是無保證的部份是零，我到期提倒轉偌濟？',
          '我提早取消，會蝕偌濟錢？'
        ]
      },
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
      hokkien: {
        checked: false,
        title: '定期存款的高利息，是按怎提到手就無彼濟？',
        script: [
          '銀行貼出來：利息比平時高真多。',
          '第一件事：彼个是一年的利息。你存三個月，提到的是四分之一。',
          '第二件事：錢鎖在內底。提早提出來，利息可能就無去。',
          '第三件事：促銷的利息通常干焦算頭一段時間，後來會落倒轉。',
          '定期存款本身是安全的。愛看予清楚的，是時間。'
        ],
        tailo: [
          'Gîn-hâng tah tshut-lâi: lī-sik pí pîng-sî kuân tsin tsē.',
          'Tē-it kiānn sū: hit ê sī tsi̍t nî ê lī-sik. Lí tshûn sann kò gue̍h, the̍h kàu ê sī sì-hun-tsi-it.',
          'Tē-nn̄g kiānn sū: tsînn só tī lāi-té. Thê-tsá the̍h tshut-lâi, lī-sik khó-lîng tō bô khì.',
          'Tē-sann kiānn sū: tshiok-siau ê lī-sik thong-siông kan-na sǹg thâu tsi̍t tuānn sî-kan, āu-lâi ē lak tò-tńg.',
          'Tīng-kî tshûn-khuán pún-sin sī an-tsuân ê. Ài khuànn hōo tshing-tshó ê, sī sî-kan.'
        ],
        ask: [
          '這个利息算幾個月？到期以後變偌濟？',
          '我提早提錢出來，愛罰偌濟？',
          '最少愛存偌濟錢才有這个利息？'
        ]
      },
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
      hokkien: {
        checked: false,
        title: '簽名就送物件，物件的錢是啥人出的？',
        script: [
          '簽名就送超市券、送電鍋、送旅行。',
          '物件是真的，你會提到。',
          '毋過物件的錢，是對你納的保費內底出來的。',
          '一份保單你可能愛納十年、二十年；物件才值幾十箍。',
          '所以順序是：先問予清楚保單，物件最後才算。'
        ],
        tailo: [
          'Tshiam-miâ tō sàng tshiau-tshī-kuàn, sàng tiān-ko, sàng lú-hîng.',
          'Mih-kiānn sī tsin ê, lí ē the̍h kàu.',
          'M̄-koh mih-kiānn ê tsînn, sī tuì lí la̍p ê pó-huì lāi-té tshut-lâi ê.',
          'Tsi̍t hūn pó-tuann lí khó-lîng ài la̍p tsa̍p nî, jī-tsa̍p nî; mih-kiānn tsiah ta̍t kuí-tsa̍p khoo.',
          'Sóo-í sūn-sī sī: sing mn̄g hōo tshing-tshó pó-tuann, mih-kiānn tsuè-āu tsiah sǹg.'
        ],
        ask: [
          '若是我毋愛物件，保費會使較俗一點無？',
          '這份保單我愛納幾年？攏總偌濟錢？',
          '我會使帶資料轉去厝看幾工才決定無？'
        ]
      },
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
      hokkien: {
        checked: false,
        title: '終身保險佮定期保險，差在佗位？',
        script: [
          '兩款保險。終身的，保到你過身；定期的，保二十年抑是三十年。',
          '仝款的保額，定期的保費俗真多。',
          '終身的貴，是因為內底有一部份當做儉錢用，而彼部份的回報無一定高。',
          '佗一款好？看你欲保的是啥物，你幾歲，厝內猶有啥人靠你。'
        ],
        tailo: [
          'Nn̄g khuán pó-hiám. Tsiong-sin ê, pó kàu lí kuè-sin; tīng-kî ê, pó jī-tsa̍p nî ia̍h-sī sann-tsa̍p nî.',
          'Kāng-khuán ê pó-gia̍h, tīng-kî ê pó-huì sio̍k tsin tsē.',
          'Tsiong-sin ê kuì, sī in-uī lāi-té ū tsi̍t pōo-hūn tòng-tsò khiām-tsînn iōng, jî hit pōo-hūn ê huê-pò bô it-tīng kuân.',
          'Tó tsi̍t khuán hó? Khuànn lí beh pó ê sī siánn-mih, lí kuí huè, tshù-lāi iáu ū siánn-lâng khò lí.'
        ],
        ask: [
          '仝款的保額，定期保險的保費是偌濟？請你算予我看。',
          '這份保單內底，偌濟是保障，偌濟是儉錢？',
          '我這个年歲，猶需要新的人壽保險無？'
        ]
      },
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
      hokkien: {
        checked: false,
        title: '賣保險的賣這份保單，伊趁偌濟？',
        script: [
          '賣保險的幫你買保險，伊會提佣金。這是正常的，毋是騙人。',
          '毋過無仝的產品，佣金無仝款。佣金高的，伊可能會先介紹予你。',
          '你會使直接問伊。這是你的權利，問了無失禮。'
        ],
        tailo: [
          'Bē pó-hiám ê pang lí bé pó-hiám, i ē the̍h iong-kim. Tse sī tsìng-siông ê, m̄ sī phiàn-lâng.',
          'M̄-koh bô-kāng ê sán-phín, iong-kim bô kāng-khuán. Iong-kim kuân ê, i khó-lîng ē sing kài-siāu hōo lí.',
          'Lí ē-sái ti̍t-tsiap mn̄g i. Tse sī lí ê kuân-lī, mn̄g liáu bô sit-lé.'
        ],
        ask: [
          '你賣這份保單，佣金大概偌濟？',
          '猶有較俗的選擇無？是按怎你推薦這一个？',
          '你是代表一間公司，抑是真多間？'
        ]
      },
      ask: [
        '你卖这份保单，佣金大概多少？',
        '还有没有更便宜的选择？为什么你推荐这一个？',
        '你是代表一家公司，还是很多家？'
      ]
    }
  ]
};
