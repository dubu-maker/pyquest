// 두 숫자를 더하는 함수
function sum(a: number, b: number): number {
    return a + b;
}

const num1: number = 10;
const num2: number = 20;
const result: number = sum(num1, num2);

// 결과를 콘솔에 출력
console.log(`Sum: ${result}`);

// 결과를 웹 페이지에 출력
document.getElementById('output')!.innerText = `The sum of ${num1} and ${num2} is ${result}`;
