var time=0, question_number=0, points=0;
function timer_start(){
    time++
    var text=document.getElementById('timer');
    text.innerHTML="Затрачено часу: "+time+" с";
}

function TimerOn(){
    timer=setInterval(timer_start, 1000);
    document.getElementById('returntostart').hidden=false;
    document.getElementById('answ1').style.display="inline-block";
    document.getElementById('answ2').style.display="inline-block"; 
    document.getElementById('answ3').style.display="inline-block";
    document.getElementById('answ4').style.display="inline-block";
    document.getElementById('start').hidden=true;
    document.getElementById('question').hidden=false;
    document.getElementById('truefalse').hidden=false;
    New_questions()
    
}

function New_questions(){
    var ques=document.getElementById('question');
    var answ1=document.getElementById('answ1');
    var answ2=document.getElementById('answ2');
    var answ3=document.getElementById('answ3');
    var answ4=document.getElementById('answ4');
    ques.innerHTML=qa[question_number][0]
    answ1.innerHTML=qa[question_number][1]
    answ2.innerHTML=qa[question_number][2]
    answ3.innerHTML=qa[question_number][3]
    answ4.innerHTML=qa[question_number][4]
}

function TimerOff(){
    document.getElementById('returntostart').hidden=true;
    document.getElementById('answ1').style.display="none";
    document.getElementById('answ2').style.display="none"; 
    document.getElementById('answ3').style.display="none";
    document.getElementById('answ4').style.display="none";
    document.getElementById('start').hidden=false;
    clearInterval(timer);
    time=0;
    var text=document.getElementById('timer');
    text.innerHTML="Затрачено часу: "+time+" с";
    document.getElementById('question').hidden=true;
    document.getElementById('truefalse').hidden=true;
    document.getElementById('truefalse').innerHTML=""
    question_number=0
    points=0
    
}

function start_hide(){
    document.getElementById('returntostart').hidden=true;
    document.getElementById('answ1').style.display="none";
    document.getElementById('answ2').style.display="none"; 
    document.getElementById('answ3').style.display="none";
    document.getElementById('answ4').style.display="none";
}

document.addEventListener("DOMContentLoaded", start_hide);

//Перевірка відповідей

function answering(obj){
    var check_answer=document.getElementById(obj).textContent;
    var answer_id=qa[question_number][5];
    var no=document.getElementById('truefalse');
    if (check_answer==qa[question_number][answer_id]){
        points++
        no.innerHTML="Правильно!"
        if (question_number==qa.length-1){
            game_over()
        }
        else{
            question_number++;
            New_questions()
        }  
    }
    else {
        no.innerHTML="Неправильна відповідь! Правильна відповідь: "+qa[question_number][answer_id]
        if (question_number==qa.length-1){
            game_over()
        }
        else{
            question_number++;
            New_questions()
        }
    }
}


//Питання та відповіді

let qa = [
    ["Яка область є наймолодшою?","Київська", "Донецька", "Черкаська", "Кіровоградська", 3],
    ["В якому році Україна стала незалежною?", 1993, 1991, 2000, 1989, 2],
    ["Яка область є найбільшою за площею?", "Одеська", "Дніпропетровська", "Київська", "Харківська", 1],
    ["Біля якого міста України знаходиться географічний центр Європи?", "Трускавець", "Луцьк", "Рахів", "Біла Церква", 3],
    ["Який вищий навчальний заклад України є найстаршим у Східній Європі?", "Острозька колегія", "Київський політехнічний інститут", "Чернівецький національний університет ім. Ю. Федьковича", "Києво-Могилянська академія", 1],
    ["Яке місце у світі українська мова займає за поширеністю?", "26", "107", "1", "39", 1],
    ["Хто є першим президентом незалежної України?", "Петро Порошенко", "Вітольд Фокін", "Леонід Кучма", "Леонід Кравчук", 3],
    ["Скільки лавр знаходиться на території України?", "12", "4", "1", "7", 2],
    ["У якому місті знаходиться найдавніший міст?", "Київ", "Феодосія", "Львів", "Ялта", 2],
    ["Яка мова є найбільш споріднена та близька до української?", "Російська", "Польська", "Білоруська", "Словацька", 3],
    ["В якому місті розташована найдовша набережна Європи?", "Київ", "Ялта", "Одеса", "Дніпро", 4],
    ["Якому видатному українцю поставлено найбільша кількість пам'ятників?", "Тарас Шевченко", "Богдан Хмельницький", "Юрій Кульчинцький", "Соломія Крушельницька", 1],
];


function game_over(){
    clearInterval(timer);
    document.getElementById('answ1').hidden=true;
    document.getElementById('answ1').style.display="none";
    document.getElementById('answ2').style.display="none"; 
    document.getElementById('answ3').style.display="none";
    document.getElementById('answ4').style.display="none";
    var percent=Math.round((points*100)/12);
    var result="Ви знаєте дуже мало про Україну! Перед подорожжю краще дізнатися ще щось нове...";
    document.getElementById('truefalse').innerHTML="Правильних відповідей: "+points+" з 12"+" ("+percent+"%)";
    if (percent>90) result="Ви точно знавець України!";
    if (percent>50 && percent<89) result="Досить добре, але є ще стільки цікавого!";
    document.getElementById('question').innerHTML=result
}