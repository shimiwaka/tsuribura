const setParams = () => {
     var validFlag = document.getElementById('valid').checked;
     var miniButtonFlag = document.getElementById('mini').checked;
     chrome.storage.sync.set({
        valid: validFlag,
        minibutton: miniButtonFlag
      },function () { });
}

const restoreParams = () => {
    chrome.storage.sync.get({
        valid: true,
        minibutton: true
      }, function(items) {
        document.getElementById('valid').checked = items.valid;
        document.getElementById('mini').checked = items.minibutton;
      });
}

document.addEventListener('DOMContentLoaded', restoreParams);

document.getElementById("valid").addEventListener("change", setParams);
document.getElementById("mini").addEventListener("change", setParams);