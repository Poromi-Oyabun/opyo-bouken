# 引き継ぎ書：おぴょの ぼうけん（ゲーム専用チャットへ）

## いまの状態（2026-11-09）
- 公開URL：https://poromi-oyabun.github.io/opyo-bouken/ （GitHub：Poromi-Oyabun/opyo-bouken、main に push すると Pages に反映）
- 第1〜8章まで公開ずみ。index.html 1ファイル（約90万字）＋ bgm/*.mp3。
- 第7章「きょうりゅうの じだい」：まちクリア後 → じくうの うず → ジュラき → ボス6たい → ちょうきょだい いんせき → しんの エクスカリバー → 「つづく」
  - コードは index.html の「/* ===== v7 シナリオ担当：」の かたまり（MAPS7・EN・SK・EQ・タイル・イベント・描画）
  - 絵は「/* v7 の 絵 */」の D（ChatGPTの 2×2 の 絵を tools/sprite_cut.py で 縮めたもの、i.hd=1）
  - 曲：jura / kazan / dboss / inseki（tools/bgm_loop.py で ループ化、BGMF に登録）

## 第8章「じくうの はざま」（2026-11-09 公開ずみ）
- 流れ：ジュラきの がけの うえ（jura 14,3）の「ρ」→ はざま（hazama 5,25 の いりぐちの しま）→ まんなかの とけい（Ω）で はりを 9じ・6じ・3じに → きのう・きょう・あしたの ばんにん（ボス）を たおして すなどけいを 3つ → はりを 12じ → きたの しまの クロノドン → くずれる はざま → まちの とけいとうが うごきだす エンディング・スタッフロール → まちへ（しょうごう「ときの ゆうしゃ」）
- コードは index.html の「/* ===== v8 シナリオ担当：」の かたまり（MAPS8・EN・EQ・タイル・イベント・描画）。第7章の 関数（juraTile・juraImg・juraBump・juraArrive・juraEnemy・juraRate・juraWin・bg7・drawWorld7・drawBG7・drawCut7）を 上がきして つないでいる（hazama は JURA_MAPS の なかま）
- 戦闘の なかの しかけ：battle() に kuroStart（すなどけいで 2ターン とめる）・kuroPhase2（HP はんぶんで まっか＋ばんにんの かいふく）・k===-8（まきもどし：すなどけい 3かいまで ふせぐ、そのあとは 6% かいふく）・e.frozen を 追加
- はしの タイル：ψ（12じ・きた）φ（3じ・ひがし）χ（6じ・みなみ）ς（9じ・にし）→ のびると 'H'（たて）'h'（よこ）。いりぐちの しまは いつも まんなかと つながっている（P.h8hand、さいしょは 6）
- まけたら いりぐちの「ときの いずみ」（π：HPと やるき ぜんかい＋きろく）の そばで めを さます。いりぐちの しまは てきが でない
- レベル じょうげん 160（P.h8Seen）。おすすめ：ばんにん 150〜154、クロノドン 158（HP 60000・2だんかい）
- クリアご：まちの ふんすい（υ）から ジュラき／はざまへ いける
- 絵：EI.bannin・EI.kurono などの 色ちがい（ph8）。はざまの タイル・とけい・とけいとうは コードで かいた
- 曲（bgm/yobi の もらった 曲を tools/bgm_loop.py で ループ化）：h8=Puppy_Steps（はざま）、h8boss=Heroic_Alt（ばんにん）、h8final=Heroic（クロノドン）、h8ban=nihongo_titleVariation（クロノドン 2だんかいめ）、h8end=Sunny_Shiba_Stroll（エンディング）、h8roll=nihongo_title（スタッフロール）
- 新しい P の 項目（ないときも 動く）：h8Seen・h8hand・clockSeen・kuroMet・h8Clear・h8Hint、P.beat.bnK/bnT/bnA/kuro
- つぎに やるなら：クリアごの おまけ（はざまの つよい てき・ずかん うめ）など

## きろく（セーブ）
- コマンドに「きろく」（saveCmd）。ほかに、フィールドで 6ぽ あるくごと・アプリを とじる／ほかの アプリへ うつるとき（visibilitychange・pagehide）に じどうで きろく。たたかいちゅう・えんしゅつちゅうは きろくしない

## まもる きまり
- 公開の まえに：python3 tools/textcheck.py index.html（誤字脱字）、python3 tools/moji_check.py（文章は キャンバスに かかない）
- 日本語の 文章は くっきりした HTML の 文字で 出す（2026-11-08 エンディングの 文字が にじむ 報告で 再発防止）
- 子どもも 楽しめる わかりやすい 展開。時間切れで ゲームオーバーに しない
- ゲームは「RPG」でなく「ゲーム」と よぶ。遊んでいる 人の セーブを こわさない（P の 新しい 項目は ないときも 動くように）
- テスト：playwright で タイトル→__G.P を いじって 各イベントを 通しで 動かす（__G.F に イベント関数を 出している）
