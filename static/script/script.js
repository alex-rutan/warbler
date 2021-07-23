"use strict";

const $body = $("body");

$body.on("click", ".like-btn", toggleLike);

function toggleLike(e) {
  e.preventDefault();

  let $target = $(e.target);
  let $star = $target;
  if ($target.hasClass("btn")) {
    $star = $target.children()
  }
  // console.log($target);
    // console.log($star);

  $star.toggleClass("fas");
  $star.toggleClass("far");
}
