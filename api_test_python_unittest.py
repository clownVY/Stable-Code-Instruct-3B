import requests

url = "http://172.17.240.85:8182/stable_code_instruct_3b"

headers = {
    'Content-Type': 'application/json'
}

java_unittest_example = """
@SpringBootTest
public class LLMProxyTest {

    @Autowired
    private LLMFactory llmFactory;

    /**
     * 会话单元测试 - 错误的案例
     */
    @Test
    public void testCompletions() {
        // 构建请求参数
        CompletionRequest completionRequest = new CompletionRequest();
        // 主要测试方法
        CompletionResult result = llmFactory.completions(completionRequest);
        // 打印结果观察
        // System.out.println(JsonHelper.toJSONString(result));
        // 验证请求结果
        Assert.assertTrue(result.isSuccess());
    }

    /**
     * 流式会话单元测试 - 正常的案例
     *
     */
    @Test
    public void testCompletionsNorma() {
        // 构建请求参数
        CompletionRequest completionRequest = new CompletionRequest();
        completionRequest.setModel(ModelEnum.open_gpt_35_turbo.getModelFull());
        completionRequest.setUserId("123456");
        completionRequest.setSystemId("123456");
        completionRequest.setStream(false);
        List<CompletionMessage> messages = new ArrayList<>();
        messages.add(new CompletionMessage("user", "广州今天天气"));
        completionRequest.setMessages(messages);
        // 主要测试方法
        CompletionResult result = llmFactory.completions(completionRequest);
        // 打印结果观察
        // System.out.println(JsonHelper.toJSONString(result));
        // 验证请求结果
        Assert.assertTrue(result.isSuccess());
    }
}
"""


def main1():
    """读取代码"""
    with open("code_python.txt", "r", encoding="utf-8") as f:
        function_to_test = f.read()
    # function_to_test = """
    # def sum_of_list(lst):
    #     return sum(lst)
    # """
    """第一步：解释代码"""
    explain_system_message = {
        "role": "system",
        "content": "You are a world-class Python developer with an eagle eye for unintended bugs and edge cases. You carefully explain code with great detail and accuracy. You organize your explanations in markdown-formatted, bulleted lists.",
    }
    explain_user_message = {
        "role": "user",
        "content": f"""Please explain the following Python function. Review what each element of the function is doing precisely and what the author's intentions may have been. Organize your explanation as a markdown-formatted, bulleted list.
        
```python
{function_to_test}
```"""
    }
    explain_messages = [explain_system_message, explain_user_message]

    explanation = requests.post(url, headers=headers, json={'message': explain_messages})
    print("=======step1==========\n", explanation, "\n=================\n")
    print("=================\n", explanation.json(), "\n=================\n")

    explain_assistant_message = {"role": "assistant", "content": explanation.json()}
    """第二步：制定计划"""
    plan_user_message = {
        "role": "user",
        "content": f"""A good unit test suite should aim to:
    - Test the function's behavior for a wide range of possible inputs
    - Test edge cases that the author may not have foreseen
    - Take advantage of the features of `pyunit` to make the tests easy to write and maintain
    - Be easy to read and understand, with clean code and descriptive names
    - Be deterministic, so that the tests always pass or fail in the same way

    To help unit test the function above, list diverse scenarios that the function should be able to handle (and under each scenario, include a few examples as sub-bullets).""",
    }

    plan_messages = [
        explain_system_message,
        explain_user_message,
        explain_assistant_message,
        plan_user_message,
    ]

    plan = requests.post(url, headers=headers, json={'message': plan_messages})
    print("=======step2==========\n", plan, "\n=================\n")
    print("=================\n", plan.json(), "\n=================\n")
    plan_assistant_message = {"role": "assistant", "content": plan.json()}

    elaboration_assistant_message = None
    """optional：如果计划太短，要求增加计划内容"""
    elaboration_user_message = {
        "role": "user",
        "content": f"""In addition to those scenarios above, list a few rare or unexpected edge cases (and as before, under each edge case, include a few examples as sub-bullets).""",
    }
    elaboration_messages = [
        explain_system_message,
        explain_user_message,
        explain_assistant_message,
        plan_user_message,
        plan_assistant_message,
        elaboration_user_message,
    ]
    elaboration = requests.post(url, headers=headers, json={'message': elaboration_messages})
    print("======step2-2===========\n", elaboration, "\n=================\n")
    print("=================\n", elaboration.json(), "\n=================\n")
    elaboration_assistant_message = {"role": "assistant", "content": elaboration.json()}
    """optional"""

    """第三步：执行计划，生成测试代码"""
    package_comment = "# below, each test case is represented by a tuple passed to the @pytest.mark.parametrize decorator"
    execute_system_message = {
        "role": "system",
        "content": "You are a world-class Python developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.",
    }
    execute_user_message = {
        "role": "user",
        "content": f"""Using Python and the `pyunit` package, write a suite of unit tests for the function, following the cases above. Include helpful comments to explain each line. Reply only with code, formatted as follows:

    ```python
    # imports
    import pyunit  # used for our unit tests
    {{insert other imports as needed}}

    # function to test
    {function_to_test}

    # unit tests
    {package_comment}
    {{insert unit test code here}}
    ```""",
    }

    execute_messages = [
        execute_system_message,
        explain_user_message,
        explain_assistant_message,
        plan_user_message,
        plan_assistant_message,
    ]
    if elaboration_assistant_message is not None:
        execute_messages += [elaboration_user_message, elaboration_assistant_message]
    execute_messages += [execute_user_message]

    execution = requests.post(url, headers=headers, json={'message': execute_messages})
    print("=====step3============\n", execution, "\n=================\n")
    print("=================\n", execution.json(), "\n=================\n")
    """第四步：检查测试代码"""
    code = execution.json().split("```python")[1].split("```")[0].strip()
    check_system_message = {
        "role": "system",
        "content": "You are a world-class Python developer with an eagle eye for unintended bugs and edge cases. You carefully review code for errors and inefficiencies. You organize your feedback in markdown-formatted, bulleted lists.",
    }
    check_user_message = {
        "role": "user",
        "content": f"""Please review the unit tests for the function. Check for any errors or inefficiencies in the code. Organize your feedback as a markdown-formatted, bulleted list.
```python
{code}
```"""
    }
    check_messages = [check_system_message, check_user_message]
    check = requests.post(url, headers=headers, json={'message': check_messages})
    print("====step4=============\n", check, "\n=================\n")
    print("=================\n", check.json(), "\n=================\n")


def main2():
    """读取代码"""
    with open("code_java.txt", "r", encoding="utf-8") as f:
        function_to_test = f.read()
    # function_to_test = """
    # def sum_of_list(lst):
    #     return sum(lst)
    # """

    """第一步：解释代码"""
    explain_system_message = {
        "role": "system",
        "content": "You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You carefully explain code with great detail and accuracy. You organize your explanations in markdown-formatted, bulleted lists.",
    }
    explain_user_message = {
        "role": "user",
        "content": f"""Please explain the following Java function. Review what each element of the function is doing precisely and what the author's intentions may have been. Organize your explanation as a markdown-formatted, bulleted list.

```java
{function_to_test}
```"""
    }
    explain_messages = [explain_system_message, explain_user_message]

    explanation = requests.post(url, headers=headers, json={'message': explain_messages})
    print("=======step1==========\n", explanation, "\n=================\n")
    print("=================\n", explanation.json(), "\n=================\n")

    explain_assistant_message = {"role": "assistant", "content": explanation.json()}

    """第二步：制定计划"""
    plan_user_message = {
        "role": "user",
        "content": f"""A good unit test suite should aim to:
    - Test the function's behavior for a wide range of possible inputs
    - Test edge cases that the author may not have foreseen
    - Take advantage of the features of `junit` to make the tests easy to write and maintain
    - Be easy to read and understand, with clean code and descriptive names
    - Be deterministic, so that the tests always pass or fail in the same way

    To help unit test the function above, list diverse scenarios that the function should be able to handle (and under each scenario, include a few examples as sub-bullets).""",
    }

    plan_messages = [
        explain_system_message,
        explain_user_message,
        explain_assistant_message,
        plan_user_message,
    ]

    plan = requests.post(url, headers=headers, json={'message': plan_messages})
    print("=======step2==========\n", plan, "\n=================\n")
    print("=================\n", plan.json(), "\n=================\n")
    plan_assistant_message = {"role": "assistant", "content": plan.json()}

    elaboration_assistant_message = None
    elaboration_user_message = None
    """optional：如果计划太短，要求增加计划内容"""
    # elaboration_user_message = {
    #     "role": "user",
    #     "content": f"""In addition to those scenarios above, list a few rare or unexpected edge cases (and as before, under each edge case, include a few examples as sub-bullets).""",
    # }
    # elaboration_messages = [
    #     explain_system_message,
    #     explain_user_message,
    #     explain_assistant_message,
    #     plan_user_message,
    #     plan_assistant_message,
    #     elaboration_user_message,
    # ]
    # elaboration = requests.post(url, headers=headers, json={'message': elaboration_messages})
    # print("======step2-2===========\n", elaboration, "\n=================\n")
    # print("=================\n", elaboration.json(), "\n=================\n")
    # elaboration_assistant_message = {"role": "assistant", "content": elaboration.json()}
    """optional"""

    """第三步：执行计划，生成测试代码"""
    package_comment = ""
    execute_system_message = {
        "role": "system",
        "content": "You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.",
    }
    execute_user_message = {
        "role": "user",
        "content": f"""Using Java and the `JUnit` package, write a suite of unit tests for the function, following the cases above. Include helpful comments to explain each line. Please follow this example:
        ```java
        {java_unittest_example}
        ```
        """,
    }

    execute_messages = [
        execute_system_message,
        explain_user_message,
        explain_assistant_message,
        plan_user_message,
        plan_assistant_message,
    ]
    if elaboration_assistant_message is not None:
        execute_messages += [elaboration_user_message, elaboration_assistant_message]
    execute_messages += [execute_user_message]

    execution = requests.post(url, headers=headers, json={'message': execute_messages})
    print("=====step3============\n", execution, "\n=================\n")
    print("=================\n", execution.json(), "\n=================\n")

    """第四步：检查测试代码"""
    code = execution.json().split("```java")[1].split("```")[0].strip()
    check_system_message = {
        "role": "system",
        "content": "You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You carefully review code for errors and inefficiencies. You organize your feedback in markdown-formatted, bulleted lists.",
    }
    check_user_message = {
        "role": "user",
        "content": f"""Please review the unit tests for the function. Check for any errors or inefficiencies in the code. Organize your feedback as a markdown-formatted, bulleted list.
```java
{code}
```"""
    }
    check_messages = [check_system_message, check_user_message]
    check = requests.post(url, headers=headers, json={'message': check_messages})
    print("====step4=============\n", check, "\n=================\n")
    print("=================\n", check.json(), "\n=================\n")


def main3():
    """读取代码"""
    with open("code_java.txt", "r", encoding="utf-8") as f:
        function_to_test = f.read()

    explain_system_message = {
        "role": "system",
        "content": "You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You carefully explain code with great detail and accuracy. You organize your explanations in markdown-formatted, bulleted lists.",
    }
    explain_user_message = {
        "role": "user",
        "content": f"""Please explain the following Java function. Review what each element of the function is doing precisely and what the author's intentions may have been. Organize your explanation as a markdown-formatted, bulleted list.

    ```java
    {function_to_test}
    ```"""
    }
    plan_user_message = {
        "role": "user",
        "content": f"""A good unit test suite should aim to:
    - Test the function's behavior for a wide range of possible inputs
    - Test edge cases that the author may not have foreseen
    - Take advantage of the features of `junit` to make the tests easy to write and maintain
    - Be easy to read and understand, with clean code and descriptive names
    - Be deterministic, so that the tests always pass or fail in the same way

    To help unit test the function above, list diverse scenarios that the function should be able to handle (and under each scenario, include a few examples as sub-bullets).""",
    }
    execute_system_message = {
        "role": "system",
        "content": "You are a world-class Java developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.",
    }
    execute_user_message = {
        "role": "user",
        "content": f"""Using Java and the `JUnit` package, write a suite of unit tests for the function, following the cases above. Include helpful comments to explain each line. Please don't use mock and follow this example:
        ```java
        {java_unittest_example}
        ```
        function to test:
        '''java
        {function_to_test}
        '''
        """,
    }

    message = [execute_system_message, execute_user_message]
    res = requests.post(url, headers=headers, json={'message': message})
    print(res.json())

def main4():
    with open("code_python.txt", "r", encoding="utf-8") as f:
        function_to_test = f.read()

    execute_system_message = {
        "role": "system",
        "content": "You are a world-class Python developer with an eagle eye for unintended bugs and edge cases. You write careful, accurate unit tests. When asked to reply only with code, you write all of your code in a single block.",
    }
    execute_user_message = {
        "role": "user",
        "content": f"""Using Python and the `PyUnit` package, write a suite of unit tests for the function, following the cases above. Include helpful comments to explain each line. 
        function to test:
        '''python
        {function_to_test}
        '''
        """,
    }

    message = [execute_system_message, execute_user_message]
    res = requests.post(url, headers=headers, json={'message': message})
    print(res.json())

if __name__ == '__main__':
    # main1()
    # main2()
    # main3()
    main4()
    """
    Here is a suite of unit tests for the `resize_image` function using Python's `unittest` package.

```python
import unittest
from PIL import Image
import numpy as np

def resize_image(im, width, height, resize_mode=1):

    Resizes an image with the specified resize_mode, width, and height.

    Args:
        resize_mode: The mode to use when resizing the image.
            0: Resize the image to the specified width and height.
            1: Resize the image to fill the specified width and height, maintaining the aspect ratio, and then center the image within the dimensions, cropping the excess.
            2: Resize the image to fit within the specified width and height, maintaining the aspect ratio, and then center the image within the dimensions, filling empty with data from image.
        im: The image to resize.
        width: The width to resize the image to.
        height: The height to resize the image to.


    im = Image.fromarray(im)

    def resize(im, w, h):
        return im.resize((w, h), resample=Image.LANCZOS)

    if resize_mode == 0:
        res = resize(im, width, height)

    elif resize_mode == 1:
        ratio = width / height
        src_ratio = im.width / im.height

        src_w = width if ratio > src_ratio else im.width * height // im.height
        src_h = height if ratio <= src_ratio else im.height * width // im.width

        resized = resize(im, src_w, src_h)
        res = Image.new("RGB", (width, height))
        res.paste(resized, box=(width // 2 - src_w // 2, height // 2 - src_h // 2))

    else:
        ratio = width / height
        src_ratio = im.width / im.height

        src_w = width if ratio < src_ratio else im.width * height // im.height
        src_h = height if ratio >= src_ratio else im.height * width // im.width

        resized = resize(im, src_w, src_h)
        res = Image.new("RGB", (width, height))
        res.paste(resized, box=(width // 2 - src_w // 2, height // 2 - src_h // 2))

        if ratio < src_ratio:
            fill_height = height // 2 - src_h // 2
            if fill_height > 0:
                res.paste(resized.resize((width, fill_height), box=(0, 0, width, 0)), box=(0, 0))
                res.paste(resized.resize((width, fill_height), box=(0, resized.height, width, resized.height)), box=(0, fill_height + src_h))
        elif ratio > src_ratio:
            fill_width = width // 2 - src_w // 2
            if fill_width > 0:
                res.paste(resized.resize((fill_width, height), box=(0, 0, 0, height)), box=(0, 0))
                res.paste(resized.resize((fill_width, height), box=(resized.width, 0, resized.width, height)), box=(fill_width + src_w, 0))

    return np.array(res)

class TestResizeImage(unittest.TestCase):

    def test_resize_image_mode0(self):
        # Test resizing an image to a specific width and height with resize_mode 0
        im = np.ones((100, 100, 3))
        res = resize_image(im, 50, 50, 0)
        self.assertEqual(res.shape, (50, 50, 3))

    def test_resize_image_mode1(self):
        # Test resizing an image to a specific width and height with resize_mode 1
        im = np.ones((200, 200, 3))
        res = resize_image(im, 100, 50, 1)
        self.assertEqual(res.shape, (100, 50, 3))

    def test_resize_image_mode2(self):
        # Test resizing an image to a specific width and height with resize_mode 2
        im = np.ones((200, 200, 3))
        res = resize_image(im, 100, 50, 2)
        self.assertEqual(res.shape, (100, 50, 3))

    def test_resize_image_mode_larger(self):
        # Test resizing an image to a larger width and height with resize_mode 1
        im = np.ones((200, 200, 3))
        res = resize_image(im, 400, 200, 1)
        self.assertEqual(res.shape, (400, 200, 3))

    def test_resize_image_mode_smaller(self):
        # Test resizing an image to a smaller width and height with resize_mode 2
        im = np.ones((200, 200, 3))
        res = resize_image(im, 100, 100, 2)
        self.assertEqual(res.shape, (100, 100, 3))

    def test_resize_image_mode_maintain_ratio_larger(self):
        # Test resizing an image to a larger width and height with resize_mode 1, maintaining the aspect ratio
        im = Image.new('RGB', (300, 200))
        res = resize_image(np.array(im), 400, 200, 1)
        self.assertEqual(res.shape, (400, 200, 3))

    def test_resize_image_mode_maintain_ratio_smaller(self):
        # Test resizing an image to a smaller width and height with resize_mode 2, maintaining the aspect ratio
        im = Image.new('RGB', (300, 200))
        res = resize_image(np.array(im), 100, 100, 2)
        self.assertEqual(res.shape, (100, 100, 3))

if __name__ == '__main__':
    unittest.main()
```

This suite of unit tests covers the following cases:

1. Resizing an image to a specific width and height with `resize_mode` 0.
2. Resizing an image to a specific width and height with `resize_mode` 1.
3. Resizing an image to a specific width and height with `resize_mode` 2.
4. Resizing an image to a larger width and height with `resize_mode` 1.
5. Resizing an image to a smaller width and height with `resize_mode` 2.
6. Resizing an image to a larger width and height with `resize_mode` 1, maintaining the aspect ratio.
7. Resizing an image to a smaller width and height with `resize_mode` 2, maintaining the aspect ratio.

These tests ensure that the function is working correctly for different scenarios and edge cases.<|im_end|>
<|endoftext|>
    """