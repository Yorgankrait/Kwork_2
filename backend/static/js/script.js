// script.js
function toggleImage(identifier) {
  const modal = document.getElementById(`imageModal-${identifier}`);

  if (modal.style.display === "flex") {
    modal.style.opacity = "0";
    setTimeout(() => {
      modal.style.display = "none";
    }, 500);
  } else {
    modal.style.display = "flex";
    setTimeout(() => {
      modal.style.opacity = "1";
    }, 10);
  }
}

window.onclick = function (event) {
  const modals = document.querySelectorAll(".modal");
  modals.forEach((modal) => {
    if (event.target === modal) {
      modal.style.opacity = "0";
      setTimeout(() => {
        modal.style.display = "none";
      }, 500);
    }
  });
};

function closeImage(identifier) {
  const modal = document.getElementById(`imageModal-${identifier}`);
  modal.style.opacity = "0";
  setTimeout(() => {
    modal.style.display = "none";
  }, 500);
}

function updateHeader() {
  const header = document.querySelector(".count");

  if (window.innerWidth > 600) {
    header.textContent = "Количество";
  } else {
    header.textContent = "Кол-во";
  }
}

updateHeader();

window.addEventListener("resize", updateHeader);

const likeButton = document.getElementById("like-button");
const dislikeButton = document.getElementById("dislike-button");

function setActive(button) {
  likeButton.classList.remove("active");
  dislikeButton.classList.remove("active");

  button.classList.add("active");

  // Обновляем изображения сразу
  updateButtonImages();
}

function updateButtonImages() {
  const likeImage = likeButton.querySelector("img");
  const dislikeImage = dislikeButton.querySelector("img");

  if (likeButton.classList.contains("active")) {
    likeImage.src = likeButton.dataset.likeImg; // Получаем путь из data-like-img
    dislikeImage.src = dislikeButton.dataset.dislikeImg; // Получаем путь из data-dislike-img
  } else {
    likeImage.src = dislikeButton.dataset.dislikeImg; // Получаем путь из data-dislike-img
    dislikeImage.src = likeButton.dataset.likeImg; // Получаем путь из data-like-img
  }
}

likeButton.addEventListener("click", function () {
  setActive(likeButton);
  rateOrder("{{ order.uuid }}", true);
});

dislikeButton.addEventListener("click", function () {
  setActive(dislikeButton);
  rateOrder("{{ order.uuid }}", false);
});

