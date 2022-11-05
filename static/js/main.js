const hideCtrl = () => {
    let ctrls = document.getElementsByClassName("swiper-ctrl");
    if(ctrls){
        for(let k = 0; k < ctrls.length; k++){
            if(ctrls[k].style.display != "none"){
                ctrls[k].style.display ="none";
            } else {
                ctrls[k].style.display ="block";
            }
        }
    }
}

const loadingSwitch = (id, on) => {
    if(on){
        document.getElementById(id).style.display = "none";
        document.getElementById(id + "_loading").style.display = "inline-block";
    } else {
        document.getElementById(id).style.display = "inline-block";
        document.getElementById(id + "_loading").style.display = "none";
    }
}

/*
const deepReload = () => {
    loadingSwitch("deep_reload",true);
}
*/

const favTweet = () => {
    let target = "../fav/" + document.getElementById("tweet_id").value;
    let request = new XMLHttpRequest();
    request.open('GET', target, true);

    loadingSwitch("favorite",true);

    request.onload = function() {
        loadingSwitch("favorite",false);
    };
    request.onerror = function() {
        loadingSwitch("favorite",false);
    };
    
    request.send();
}

const reTweet = () => {
    let target = "../rt/" + document.getElementById("tweet_id").value;
    let request = new XMLHttpRequest();
    request.open('GET', target, true);

    loadingSwitch("retweet",true);

    request.onload = function() {
        loadingSwitch("retweet",false);
    };
    request.onerror = function() {
        loadingSwitch("retweet",false);
    };
    
    request.send();
}

const favTweets = () => {
    let target = location.href.replace('/show/','/fav_all/')
    let request = new XMLHttpRequest();
    request.open('GET', target, true);
    document.getElementById("result_area").innerHTML = "いいね中です……";
    loadingSwitch("favorite_all",true);

    request.onload = function() {
        loadingSwitch("favorite_all",false);    
        if (this.status >= 200 && this.status < 400) {
            let response = JSON.parse(this.response);
            if(response.success){
                document.getElementById("result_area").innerHTML = response.message;
            } else {
                document.getElementById("result_area").innerHTML = response.message;
            }
        } else {
            document.getElementById("result_area").innerHTML = "通信に失敗しました……";
        }
    };
    
    request.onerror = function() {
        loadingSwitch("favorite_all",false);    
        document.getElementById("result_area").innerHTML = "通信に失敗しました……";
    };
    
    request.send();
}


const reTweets = () => {
    let target = location.href.replace('/show/','/rt_all/')
    let request = new XMLHttpRequest();
    request.open('GET', target, true);
    document.getElementById("result_area").innerHTML = "リツイート中です……";
    loadingSwitch("retweet_all",true);
    
    request.onload = function() {
        loadingSwitch("retweet_all",false);
        if (this.status >= 200 && this.status < 400) {
            let response = JSON.parse(this.response);
            if(response.success){
                document.getElementById("result_area").innerHTML = response.message;
            } else {
                document.getElementById("result_area").innerHTML = response.message;
            }
        } else {
            document.getElementById("result_area").innerHTML = "通信に失敗しました……";
        }
    };
    
    request.onerror = function() {
        loadingSwitch("retweet_all",false);
        document.getElementById("result_area").innerHTML = "通信に失敗しました……";
    };
    
    request.send();
}

window.onload = function () {
    let slides = document.getElementsByClassName("swiper-slide");
    for( let i = 0; i < slides.length; i++ ) {
        slides[i].onclick = hideCtrl;
    }
    document.getElementById("favorite_all_button").addEventListener("click", favTweets);
    document.getElementById("retweet_all_button").addEventListener("click", reTweets);
   //document.getElementById("deep_reload_button").addEventListener("click", deepReload);
}