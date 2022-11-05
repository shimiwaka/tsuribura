// 定数定義
const INTERVAL_TIME = 800;
const VIEWER_URL = "https://peraimaru.site/show/";
const TWEET_URL_RE = /(\/[a-zA-Z0-9_]+)\/status\/([0-9]+)$/;
const BUTTON_STYLE = `
                    margin: 0 0 0 20px;
                    text-align:center;
                    background-color:#49a9d4;
                    border:0;
                    padding: 5px 25px 5px 25px;
                    color: #fff;
                    font-size : 16px;
                    border-radius:5px;
                    cursor: pointer;
                    `;
const BUTTON_STYLE_MINI = `
                    margin: 0 0 0 10px;
                    text-align:center;
                    background-color:#49a9d4;
                    border:0;
                    padding: 1px 5px 1px 5px;
                    color: #fff;
                    border-radius:5px;
                    cursor: pointer;
                    `;

// 設定フラグ
let isValid = true;
let MiniButtonIsValid = true;

let pageInitCheckTimer = null;

// function
// ビューワにジャンプする
const jumpToViewer = (e) => window.open(VIEWER_URL + e.target.eventParam);

// function
// ツイートツリーを全部取得
const getTweetTree = () => document.querySelectorAll("#react-root main section article");

// function
// 設定を読み込み
const loadConfig = () => {
    chrome.storage.sync.get({
        valid: true,
        minibutton: true,
      }, function(items) {
        isValid = items.valid;
        MiniButtonIsValid = items.minibutton;
    });
}

// function
// ツイートが画像を持っているかどうか
const hasImage = (screen_name, tweet) => {
    let links = tweet.querySelectorAll("a[href^='" + screen_name + "/']");
    let tweet_id = null;
    let count = 0;
    if(links){
        for( let j = 0; j < links.length; j++){
            let link_href = links[j].getAttribute('href');
            if(link_href){
                let r = link_href.match(screen_name + "\/status\/([0-9]+)\/photo\/[0-9]");
                if(r){ tweet_id = r[1]; }
            }
        }
    }
    if(tweet_id){
        return tweet_id;
    }
    return null;
}

// function
// スクリーンネーム取得
const getScreenName = () => {
    let isMatch = document.URL.match(TWEET_URL_RE);
    if (!isMatch){
        return null;
    }
    return isMatch[1];
}

// function
// 一番うしろのツイートを抽出
const getLastTweet = () => {
    const screen_name = getScreenName();
    if (!screen_name){ return null; }
    let tweets = getTweetTree();
    let tweet_count = 0;
    let last_id = "0";

    for(var i = 0; i < tweets.length; i++){
        let tweet = tweets[i];
        let tweet_id = hasImage(screen_name, tweet);
        if(tweet_id){
            tweet_count++;
            if(tweet_id.localeCompare(last_id) > 0){
                last_id = tweet_id;
            }
        }
    }
    if(tweet_count < 1){
        return null;
    }
    return last_id;
}

// function
// ボタン設置済みか確認
const isAlreadySet = (area) => {
    if(area.querySelector("input#open_viewer_button")){
        return true;
    } else {
        return false;
    }
}

// function
// メインツイートにボタン設置
const setButton = (area, last_id, size) => {
    if(!isAlreadySet(area)){
        let jump_button = document.createElement("input");
        jump_button.setAttribute('type', 'button');
        jump_button.setAttribute('id', 'open_viewer_button');
        jump_button.setAttribute('value', '一気読み');
        jump_button.setAttribute('style', BUTTON_STYLE);
        if (size == "MINI"){
            jump_button.setAttribute('style', BUTTON_STYLE_MINI);
        }
        jump_button.addEventListener("click", jumpToViewer);
        jump_button.eventParam = last_id;
        area.appendChild(jump_button);
    }
}

// fucntion
// ボタンの設置位置特定
const setTypeDesc = (last_id) => {
    const screen_name = getScreenName();
    if (!screen_name){ return null; }

    let count = 0;
    let tweets = getTweetTree();
    for (let i = 0; i < tweets.length; i++){
        let tweet = tweets[i];
        if(hasImage(screen_name, tweet)){
            count++;
        }
    }
    if(count > 1){
        for (let i = 0; i < tweets.length; i++){
            let tweet = tweets[i]
            let button_area = tweet.querySelector('div[role="group"]');
            let client_link = tweet.querySelector("a[href^='https://help.twitter.com']");
            if(hasImage(screen_name, tweet)){
                if(client_link){
                    setButton(client_link.parentNode, last_id, "NORMAL");
                } else if(button_area && MiniButtonIsValid){
                    setButton(button_area, last_id, "MINI");
                }
            }
        }
    }
}

// function
// ロード完了と判断された時
const loadComplete = () => {
    clearInterval(pageInitCheckTimer);
    loading = false;
    let last_id = getLastTweet();
    if(last_id && isValid){
        setTypeDesc(last_id);
    }
}

// function
// メイン
const main = (e) => {
    pageInitCheckTimer = setInterval(loadComplete, INTERVAL_TIME);
    loadConfig();
    let loading = true;
    let href = location.href;
    let observer = new MutationObserver(function(mutations) {
        // アドレスが変化してたらロード中に戻す
        if(href !== location.href) {
            loading = true;
            href = location.href;
        }
        // ロード中ならタイマーをもとに戻す
        if(loading){
            clearInterval(pageInitCheckTimer);
            // 一定時間DOMが変化しなければロード完了とみなす
            pageInitCheckTimer = setInterval(loadComplete, INTERVAL_TIME);
        }
    });
    observer.observe(document, { childList: true, subtree: true });
};

// 初期化
window.addEventListener("load", main, false);