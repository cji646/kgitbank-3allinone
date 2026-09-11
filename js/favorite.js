(function() {

    var FAVORITE_KEY = "favoriteCountry";


    /* =========================
       관심 국가 설정 / 해제
    ========================= */
    window.toggleFavoriteCountry = function(country) {

        var savedCountry =
            localStorage.getItem(FAVORITE_KEY);

        /*
         * 현재 페이지가 이미 관심 국가라면
         * 다시 클릭했을 때 해제
         */
        if (savedCountry === country) {

            localStorage.removeItem(FAVORITE_KEY);

            updateFavoriteButtons();

            alert("관심 국가 설정이 해제되었습니다.");

            return;
        }


        /*
         * 다른 국가가 이미 선택돼 있어도
         * 새 국가로 덮어씀
         *
         * 따라서 항상 하나만 저장됨
         */
        localStorage.setItem(
            FAVORITE_KEY,
            country
        );

        updateFavoriteButtons();

        alert("관심 국가로 설정되었습니다.");
    };


    /* =========================
       메인페이지 관심 국가 이동
    ========================= */
    window.goFavoriteCountry = function() {

        var country =
            localStorage.getItem(FAVORITE_KEY);

        if (!country) {

            alert("설정된 관심 국가가 없습니다.");

            return;
        }


        if (country === "korea") {

            location.href = "korea.html";

        }
        else if (country === "japan") {

            location.href = "japan.html";

        }
        else if (country === "vietnam") {

            location.href = "vietnam.html";
        }
    };


    /* =========================
       버튼 표시 갱신
    ========================= */
    function updateFavoriteButtons() {

        var savedCountry =
            localStorage.getItem(FAVORITE_KEY);

        var buttons =
            document.querySelectorAll(
                ".country-favorite-btn"
            );

        var i;

        for (i = 0; i < buttons.length; i++) {

            var button = buttons[i];

            var country =
                button.getAttribute(
                    "data-country"
                );


            if (country === savedCountry) {

                button.className =
        	     "country-favorite-btn account-btn secondary-btn favorite-active";
                button.innerHTML =
                    "♥ 관심 국가";

            } else {

                button.className =
        	"country-favorite-btn account-btn secondary-btn";
                button.innerHTML =
                    "♡ 관심 국가";
            }
        }
    }


    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            updateFavoriteButtons
        );

    } else {

        updateFavoriteButtons();
    }

})();
