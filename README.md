Код должен быть максимально простой и с пояснениями не делая ничего лишнего делай только то что я скажу если хочешь сделать что-то еще то прежде всего согласовываем эти действия.
Отвечай по-русски. Отвечай лаконично. Сначала обсуждаем а потом делаем. Пишем код в среде программирования nodered 3.02 Работа строится следующим образом я ставлю задачу сначала Обсуждаем что нужно сделать а потом делаем ты мне присылаешь полный файл с кодом. Пиши на веб интерфейсе название версии. название версии должно включать текущую дату год число а также текущее время часы минуты - только непрерывный ряд цифр то есть получается число в формате флоат. На отдельном дашборде пишем название версии и историю версий текущей версии и сохраняем историю предыдущих версий Какие изменения были выполнены в той или иной версии3.0.2 - версия. node-red находится в модуле адам 6717 фирмы advantech этот модуль взаимодействует с другим модулем 6224 адам фирмы advantech и панелью оператора weintek cmt820 все последующие имена и версии файлов должны формироваться следующим образом: название файла с кодом должно быть например такое - 231020251107.json - непрерывный ряд цифр то есть получается число в формате флоат . Где первые две цифры – это текущее число. Следующие две цифры это текущий месяц. Следующие четыре цифры – это текущий год. Следующие две цифры – это текущее время час. Следующие две цифры – это текущее время минуты.
Сообщения на дэшборде Должно быть таким - Текущая версия: 231020251107. тогда глобальная переменная с именем VER = 231020251107 имя файла, названия версии И значение переменной VER должны совпадать например имя файла - 231020251107.json, имя версии - 231020251107, VER=231020251107 имя я буду задавать вручную при задании на изменение кода
Создаем проект “контроллер итерации” в среде программирования  node-red версия 3.02.
node-red находится в модуле adam  6717 фирмы advantech этот модуль взаимодействует с другим модулем 6224 adam фирмы advantech
Данные передаются  в панель оператора фирмы weintek cmt-fhdx-820.
Для передачи данных (Значение всех глобальных переменных) в панель оператора  в модуле 6717 организуется сервер  и данные передаются по Изернет.
Все комментарии пишем по-русски. Надписи на Веб интерфейсе по русски.
Цель проекта создание контроллера итерации.
Контроллер итерации должен выполнять 5 шагов итерации.
Для каждого шага Итерации задаются параметры итерации: 
начальное значение – например минус 1000
скорость– например 100 Миллисекунд
шаг — например 100
конечное  значение —например 1000
пауза после конечного значения итерации —например 0 миллисекунд.
Итерация должна происходить следующим образом: Задается начальное значение. Через время = скорость. Задается  следующее значение которое равно предыдущее значение плюс шаг. И так до конечного значения. Контроллер итерации должен присваивать глобальной переменной текущее значение результата итерации.
Параметры итерации при старте проекта должны. Быть вычитаны. Из файла.
Также параметры итерации (уставки) Должны иметь возможность быть установлены из веб интерфейса. Также из веб интерфейса должна быть возможность управлять процессом итерации включать выключать приостанавливать процесс итерации.
Также из веб интерфейса должна быть возможность записи в файл новых параметров итерации И вычитывание из файла параметров итерации. 
Также вы веб интерфейсе должны быть видны названия всех переменных и их Актуальные значения а также график результата итерации.
Если файла Нету То Параметры итерации Должны быть взяты по умолчанию, такие как в примере.

Параметры итерации должны быть. Глобальными переменными с соответствующими индексами  - индекс соответствует шагу итерации 1 2 3 4 5.
Также должны быть. Переменные глобальные:
-  Это Переменная -Номер шага итерации. 
- Переменная. Управление Процессом итерации (Значение один. Старт итерации. Значение ноль. Остановка итерации. Значение 2. Рестарт итерации.). 
При загрузке. Проекта итерация должна быть включена.
Шаги итерации с 1 по 5 следует один за другим и затем после 5 шага начинаются с начала с 1 шага. И так в цикле. Если задано значение скорости 0 миллисекунд то шаг пропускается.
Для Того, чтобы задавать скорость, использовать стандартную ноду – delay - (Описание:
  Delays each message passing through the node or limits the rate at which they can pass
Inputs
delaynumber
Sets the delay, in milliseconds, to be applied to the message. This option only applies if the node is configured to allow the message to override the configured default delay interval.
ratenumber
Sets the rate value in milliseconds between messages. This node overwrites the existing rate value defined in the node configuration when it receives the message which contains msg.rate value in milliSeconds. This option only applies if the node is configured to allow the message to override the configured default rate interval.
reset
If the received message has this property set to any value, all outstanding messages held by the node are cleared without being sent.
flush
If the received message has this property set to a numeric value then that many messages will be released immediately. If set to any other type (e.g. boolean), then all outstanding messages held by the node are sent immediately.
toFront
When in rate limit mode, if the received message has this property set to boolean true, then the message is pushed to the front of the queue and will be released next. This can be used in combination with msg.flush=1 to resend immediately.
Details
When configured to delay messages, the delay interval can be a fixed value, a random value within a range or dynamically set for each message. Each message is delayed independently of any other message, based on the time of its arrival.
When configured to rate limit messages, their delivery is spread across the configured time period. The status shows the number of messages currently in the queue. It can optionally discard intermediate messages as they arrive.
If set to allow override of the rate, the new rate will be applied immediately, and will remain in effect until changed again, the node is reset, or the flow is restarted.
The rate limiting can be applied to all messages, or group them according to their msg.topic value. When grouping, intermediate messages are automatically dropped. At each time interval, the node can either release the most recent message for all topics, or release the most recent message for the next topic.
Note: In rate limit mode the maximum queue depth can be set by a property in your settings.js file. For example nodeMessageBufferMaxLength: 1000,).

Также можно использовать ноду. Триггер. Вот ее описание-  trigger
When triggered, can send a message, and then optionally a second message, unless extended or reset.

Inputs
delaynumber
Sets the delay, in milliseconds, to be applied to the message. This option only applies if the node is configured to allow the message to override the configured default delay interval.
reset
If a message is received with this property, any timeout or repeat currently in progress will be cleared and no message triggered.
Details
This node can be used to create a timeout within a flow. By default, when it receives a message, it sends on a message with a payload of 1. It then waits 250ms before sending a second message with a payload of 0. This could be used, for example, to blink an LED attached to a Raspberry Pi GPIO pin.

The payloads of each message sent can be configured to a variety of values, including the option to not send anything. For example, setting the initial message to nothing and selecting the option to extend the timer with each received message, the node will act as a watchdog timer; only sending a message if nothing is received within the set interval.

If set to a string type, the node supports the mustache template syntax.

The delay between sending messages can be overridden by msg.delay if that option is enabled in the node. The value must be provided in milliseconds.

If the node receives a message with a reset property, or a payload that matches that configured in the node, any timeout or repeat currently in progress will be cleared and no message triggered.

The node can be configured to resend a message at a regular interval until it is reset by a received message.

Optionally, the node can be configured to treat messages as if they are separate streams, using a msg property to identify each stream. Default msg.topic.

The status indicates the node is currently active. If multiple streams are used the status indicates the number of streams being held.
На гитхаб формируй сообщения и коментарии на русском языке, чтобы мне было понятно. 
