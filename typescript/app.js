// 두 숫자를 더하는 함수
function sum(a, b) {
    return a + b;
}
var num1 = 10;
var num2 = 20;
var result = sum(num1, num2);
// 결과를 콘솔에 출력
console.log("Sum: ".concat(result));
// 결과를 웹 페이지에 출력
document.getElementById('output').innerText = "The sum of ".concat(num1, " and ").concat(num2, " is ").concat(result);
