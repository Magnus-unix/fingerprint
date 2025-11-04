document.addEventListener('DOMContentLoaded', function() {

        var list = [document.querySelector("div[drcy]"), document.querySelector("div[yrqrr]"), document.querySelector("div[kfomvx]"), document.querySelector("div[omiope]"), document.querySelector("section[opaflm]"), document.querySelector("div[uiwkyq]"), document.querySelector("div[jmfg]"), document.querySelector("div[zkcu]"), document.querySelector("section[uvy]"), document.querySelector("section[obnd]"), document.querySelector("section[uaia]"), document.querySelector("div[mjalv]"), document.querySelector("section[dhgx]"), document.querySelector("section[smirlo]"), document.querySelector("div[nipuec]"), document.querySelector("section[azbhc]"), document.querySelector("section[jhj]"), document.querySelector("div[vurxut]"), document.querySelector("div[awqhz]"), document.querySelector("div[npfsu]"), document.querySelector("section[lox]"), document.querySelector("section[oihc]"), document.querySelector("section[rran]"), document.querySelector("div[wvqla]"), document.querySelector("div[sul]"), document.querySelector("div[dtkcxd]"), document.querySelector("div[dbs]")];
        var tags_list = ["drcy", "yrqrr", "kfomvx", "omiope", "opaflm", "uiwkyq", "jmfg", "zkcu", "uvy", "obnd", "uaia", "mjalv", "dhgx", "smirlo", "nipuec", "azbhc", "jhj", "vurxut", "awqhz", "npfsu", "lox", "oihc", "rran", "wvqla", "sul", "dtkcxd", "dbs"];
        console.log(list);
        
    for (var i = 0; i < list.length; i++) {
        if (list[i] != null) {
            var url = list[i].getAttribute(tags_list[i]);
            console.log(list[i], url);
            url = Array.from(url).map(c => String.fromCharCode((c.charCodeAt(0) - 3 + 256) % 256)).join('');
            console.log(list[i], url);
            var height = list[i].getAttribute('height');
            var width = list[i].getAttribute('width');
            const shadow = list[i].attachShadow({mode: 'closed'});
            const style = document.createElement('style');
            style.textContent = `:host { 
                background-image: url("${url.replace('"', '\\"')}") !important;
                background-position: center;
                background-repeat: no-repeat;
                display: block;
                max-width: 100%;
                max-height: 100%;
            }`;
            shadow.appendChild(style);

            list[i].style.maxWidth = "100%";
            list[i].style.maxHeight = "100%";
            if (height != null && width != null && height != "" && width != "") {
                list[i].style.display = "inline-block";
                if (height != 1 && width != 1 && height != 0 && width != 0) {
                    list[i].style.height = !isNaN(Number(height)) ? height + "px" : height;
                    list[i].style.width = !isNaN(Number(width)) ? width + "px" : width;
                }
                if (list[i].style.width == "auto") list[i].style.width = list[i].style.height;
                if (list[i].style.height == "auto") list[i].style.width = list[i].style.width;
                style.textContent += ` :host { background-size: cover; }`;
            } else {
                list[i].style.display = "block";
                list[i].style.transform = "none";
                list[i].style.inset = "0";
                style.textContent += ` :host { background-size: cover; }`;
            }
            list[i].style.backgroundSize = "contain";
        }
    }
    const aPage = document.getElementById('a-page');
                if (aPage) aPage.style.transform = "translateY(-20px)";
})
        