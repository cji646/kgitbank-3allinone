"use strict";

document.addEventListener("DOMContentLoaded", function () {

    const items = document.querySelectorAll(".qna-item");
    const categoryButtons = document.querySelectorAll(".category-btn");

    const searchInput = document.getElementById("qnaSearchInput");
    const searchBtn = document.getElementById("qnaSearchBtn");
    const emptyMessage = document.getElementById("qnaEmpty");

    let selectedCategory = "all";


    /* 질문 클릭 → 답변 열기/닫기 */

    items.forEach(function (item) {

        const question = item.querySelector(".qna-question");

        question.addEventListener("click", function () {
            item.classList.toggle("active");
        });

    });


    /* 카테고리 */

    categoryButtons.forEach(function (button) {

        button.addEventListener("click", function () {

            categoryButtons.forEach(function (btn) {
                btn.classList.remove("active");
            });

            button.classList.add("active");

            selectedCategory = button.dataset.category;

            filterItems();

        });

    });


    /* 검색 버튼 */

    searchBtn.addEventListener("click", filterItems);


    /* 검색창 Enter */

    searchInput.addEventListener("keyup", function (event) {

        if (event.key === "Enter") {
            filterItems();
        }

    });


    /* 검색 + 카테고리 필터 */

    function filterItems() {

        const keyword =
            searchInput.value
                .trim()
                .toLowerCase();

        let visibleCount = 0;

        items.forEach(function (item) {

            const category = item.dataset.category;
            const text = item.innerText.toLowerCase();

            const categoryMatch =
                selectedCategory === "all" ||
                selectedCategory === category;

            const keywordMatch =
                keyword === "" ||
                text.includes(keyword);

            if (categoryMatch && keywordMatch) {

                item.style.display = "";
                visibleCount++;

            } else {

                item.style.display = "none";

            }

        });

        emptyMessage.style.display =
            visibleCount === 0
                ? "block"
                : "none";

    }


    /* 새 글 작성 */

    const writeBtn = document.getElementById("writeBtn");
    const writePanel = document.getElementById("writePanel");

    const writeCancelBtn =
        document.getElementById("writeCancelBtn");

    const writeSaveBtn =
        document.getElementById("writeSaveBtn");


    writeBtn.addEventListener("click", function () {

        writePanel.classList.add("active");

        writePanel.scrollIntoView({
            behavior: "smooth",
            block: "center"
        });

    });


    writeCancelBtn.addEventListener("click", function () {

        writePanel.classList.remove("active");

    });


    writeSaveBtn.addEventListener("click", function () {

        const title =
            document.getElementById("writeTitle")
                .value
                .trim();

        const content =
            document.getElementById("writeContent")
                .value
                .trim();

        if (!title || !content) {

            alert("제목과 내용을 입력해 주세요.");
            return;

        }

        alert(
            "작성 화면까지 구현되었습니다.\n" +
            "게시글 저장은 WAS/DB 연동 후 적용됩니다."
        );

    });

});
