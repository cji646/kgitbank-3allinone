(function() {

    var loginBtn = document.getElementById("loginBtn");
    var logoutBtn = document.getElementById("logoutBtn");
    var userInfo = document.getElementById("userInfo");
    var favoriteBtn = document.getElementById("favoriteBtn");

    if (!loginBtn || !logoutBtn || !userInfo) {
        return;
    }

    function checkLogin() {

        var xhr = new XMLHttpRequest();

        xhr.open("GET", "/me", true);
        xhr.withCredentials = true;

        xhr.onreadystatechange = function() {

            if (xhr.readyState !== 4) {
                return;
            }

            if (xhr.status === 200) {

                var data;

                try {
                    data = JSON.parse(xhr.responseText);
                } catch (e) {
                    return;
                }

                loginBtn.style.display = "none";
                logoutBtn.style.display = "inline-block";
                userInfo.style.display = "inline-block";

                if (favoriteBtn) {
                    favoriteBtn.style.display = "inline-block";
                }

                if (data.user && data.user.name) {
                    userInfo.innerHTML = data.user.name + "님";
                } else if (data.name) {
                    userInfo.innerHTML = data.name + "님";
                } else {
                    userInfo.innerHTML = "로그인 중";
                }

            } else {

                loginBtn.style.display = "inline-block";
                logoutBtn.style.display = "none";
                userInfo.style.display = "none";

                if (favoriteBtn) {
                    favoriteBtn.style.display = "none";
                }
            }
        };

        xhr.send();
    }


    logoutBtn.onclick = function() {

        var xhr = new XMLHttpRequest();

        xhr.open("POST", "/logout", true);
        xhr.withCredentials = true;

        xhr.onreadystatechange = function() {

            if (xhr.readyState !== 4) {
                return;
            }

            if (xhr.status === 200) {

                alert("로그아웃되었습니다.");

                location.href = "index.html";

            } else {

                alert("로그아웃에 실패했습니다.");
            }
        };

        xhr.send();
    };


    checkLogin();

})();
