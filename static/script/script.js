"use strict";

const $body = $("body");

$body.on("click", "i", toggleLike);

function toggleLike(e) {
  e.preventDefault();

  //   console.log(e.target);
  let $target = $(e.target);
  console.log($target);
  let $star = $target.next();
  //   console.log($star);

  $target.toggleClass("fas");
  $target.toggleClass("far");
}
