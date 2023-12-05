from typing import Dict, List, Optional
import json
from trendychat.configs import EbeddingConfig, LLMConfig
from trendychat.llm import openai_reponse, async_openai_reponse
from trendychat.messages import ChatMessage
import os
import traceback
import pandas as pd
import logging

# 配置日志记录
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

embedding_config = EbeddingConfig()
gpt_json_config = LLMConfig(json_format=True)
gpt_config = LLMConfig()


class LlmMessage:
    system: str = "You are an AI assistant that helps people find information.And please don't use simplified Chinese, use traditional Chinese."
    assistant: str = ""
    user: str = None

    @classmethod
    def generate(cls) -> List[Dict]:
        return [
            {"role": "system", "content": cls.system},
            {"role": "assistant", "content": cls.assistant},
            {"role": "user", "content": cls.user},
        ]


def generate_system_prompt(stage_name: str = "initial") -> str:
    # logging.info(f"Generating system prompt for stage_name: {stage_name}")
    if stage_name == "initial":
        variable_name = "REPORT_INITIAL_PROMPT"
        result = os.getenv("REPORT_INITIAL_PROMPT", None)
    elif stage_name == "final":
        variable_name = "REPORT_FINAL_PROMPT"
        result = os.getenv("REPORT_FINAL_PROMPT", None)
    if not result:
        raise ValueError(
            f"enviroment variable '{variable_name}' is empty, please check."
        )
    return result


def generate_assistant_prompt(
    history: List[str] = None,
    context: List[str] = None,
    analysis_description: Optional[str] = None,
    analysis_script: Optional[str] = None,
    analysis_result: Optional[str] = None,
) -> str:
    # logging.info("Generating assistant prompt")
    prompt = "contain chat log 'history' (One question and one answer) and report 'context' below: \n"
    if not context:
        context = []
    if not history:
        history = []
    content = {
        "history": history,
        "context": context,
    }
    if analysis_description:
        content["analysis_description"] = analysis_description
    if analysis_script:
        content["analysis_script"] = analysis_script
    if analysis_result:
        content["analysis_result"] = analysis_result
    prompt += str(content)
    return prompt


def analyze_question(user_text: str, history: List[str], context: List[str]) -> Dict:
    """
    get summary from gpt model with question and references,
    return {"analysis_description":"", "analysis_script":""}
    """
    logging.info("RUN 'analyze_question'")
    try:
        LlmMessage.system = generate_system_prompt()
        LlmMessage.assistant = generate_assistant_prompt(
            history=history, context=context
        )
        LlmMessage.user = user_text
        msg = LlmMessage.generate()
        model_config = gpt_json_config.get()  # 回傳json格式
        print("=====> 等待請求openai_reponse....")
        response = openai_reponse(messages=msg, model_config=model_config)
        response = response["choices"][0]["message"]["content"]
        response = json.loads(response)
    except Exception as e:
        traceback.print_exc()
        raise RuntimeError(f"An error occurred during 'analyze_question': {str(e)}")

    return response


async def analyze_question_async(
    user_text: str, history: List[str], context: List[str]
) -> Dict:
    """
    get summary from gpt model with question and references,
    return {"analysis_description":"", "analysis_script":""}
    """
    logging.info("RUN 'analyze_question_async'")
    try:
        LlmMessage.system = generate_system_prompt()

        LlmMessage.assistant = generate_assistant_prompt(
            history=history, context=context
        )
        LlmMessage.user = user_text
        msg = LlmMessage.generate()
        model_config = gpt_json_config.get()  # 回傳json格式
        print("=====> 等待請求openai_reponse....")
        response = await async_openai_reponse(messages=msg, model_config=model_config)
        response = response["choices"][0]["message"]["content"]
        response = json.loads(response)
        # 从响应中提取出消息内容
        return response
    except Exception as e:
        raise RuntimeError(
            f"An error occurred during 'analyze_question_async': {str(e)}"
        )


def execute_analysis_script(script: str) -> str:
    logging.info("RUN 'execute_analysis_script'")
    local_vars = {}
    exec(script, {}, local_vars)
    result = local_vars.get("result")
    if isinstance(result, pd.DataFrame):
        result = result.to_json()
    else:
        result = str(result)

    return result


def generate_comprehensive_response(
    user_text: str,
    history: List[str],
    context: List[str],
    analysis_description: str,
    analysis_script: str,
    analysis_result: str,
):
    logging.info("RUN 'generate_comprehensive_response'")
    try:
        LlmMessage.system = generate_system_prompt(stage_name="final")
        LlmMessage.assistant = generate_assistant_prompt(
            history=history,
            context=context,
            analysis_description=analysis_description,
            analysis_script=analysis_script,
            analysis_result=analysis_result,
        )
        LlmMessage.user = user_text
        msg = LlmMessage.generate()
        model_config = gpt_config.get()  # 回傳json格式
        print("=====> 等待請求openai_reponse....")
        response = openai_reponse(messages=msg, model_config=model_config)
        response = response["choices"][0]["message"]["content"]
        # 从响应中提取出消息内容
        return response
    except Exception as e:
        raise RuntimeError(
            f"An error occurred during 'generate_final_response': {str(e)}"
        )


async def generate_comprehensive_response_async(
    user_text: str,
    history: List[str],
    context: List[str],
    analysis_description: str,
    analysis_script: str,
    analysis_result: str,
):
    logging.info("RUN 'generate_comprehensive_response_async'")
    try:
        LlmMessage.system = generate_system_prompt(stage_name="final")
        LlmMessage.assistant = generate_assistant_prompt(
            history=history,
            context=context,
            analysis_description=analysis_description,
            analysis_script=analysis_script,
            analysis_result=analysis_result,
        )
        LlmMessage.user = user_text
        msg = LlmMessage.generate()
        model_config = gpt_config.get()  # 回傳json格式
        print("=====> 等待請求openai_reponse....")
        response = await async_openai_reponse(messages=msg, model_config=model_config)
        response = response["choices"][0]["message"]["content"]
        # 从响应中提取出消息内容
        return response
    except Exception as e:
        raise RuntimeError(
            f"An error occurred during 'generate_comprehensive_response_async': {str(e)}"
        )


class ReportChat:
    @classmethod
    def generate_initial_response(cls, message: ChatMessage) -> ChatMessage:
        logging.info("Generating initial response")
        try:
            result = analyze_question(
                user_text=message.user_text,
                history=message.history,
                context=message.context,
            )
            message.analysis_description = result["analysis_description"]
            message.analysis_script = result["analysis_script"]
        except Exception as e:
            # 记录错误信息，并给出友好的错误提示
            logging.error(
                f"Error in generate_initial_response: {traceback.format_exc()}"
            )
            message.analysis_description = (
                "Error occurred while analyzing the question."
            )
            message.analysis_script = ""
        return message

    @classmethod
    def generate_final_response(cls, message: ChatMessage) -> ChatMessage:
        logging.info("Generating final response")
        retry = 3
        while retry > 0:
            try:
                analysis_result = execute_analysis_script(
                    script=message.analysis_script
                )
                message.analysis_result = analysis_result
                break
            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                retry -= 1
                if retry > 0:
                    logging.info(
                        f"Retrying generate_initial_response (Attempt: {4 - retry})"
                    )
                    message = cls.generate_initial_response(message)
                else:
                    message.analysis_result = "Error occurred after several attempts."
                    logging.error("Exceeded maximum retry attempts")
        try:
            message.bot_text = generate_comprehensive_response(
                user_text=message.user_text,
                history=message.history,
                context=message.context,
                analysis_description=message.analysis_description,
                analysis_script=message.analysis_script,
                analysis_result=message.analysis_result,
            )
        except Exception as e:
            logging.error(f"Error during generate_comprehensive_response: {str(e)}")
            raise RuntimeError(f"Error in generate_final_response: {str(e)}")
        return message

    @classmethod
    async def async_generate_initial_response(cls, message: ChatMessage) -> ChatMessage:
        try:
            result = await analyze_question_async(
                user_text=message.user_text,
                history=message.history,
                context=message.context,
            )
            message.analysis_description = result["analysis_description"]
            message.analysis_script = result["analysis_script"]
        except Exception as e:
            # 记录错误信息，并给出友好的错误提示
            print(f"Error in generate_initial_response: {str(e)}")
            message.analysis_description = (
                "Error occurred while analyzing the question."
            )
            message.analysis_script = ""
        return message

    @classmethod
    async def async_generate_final_response(cls, message: ChatMessage) -> ChatMessage:
        logging.info("Generating final response asynchronously")
        retry = 3
        while retry > 0:
            try:
                analysis_result = execute_analysis_script(
                    script=message.analysis_script
                )
                message.analysis_result = analysis_result
                break
            except Exception as e:
                logging.error(f"Error during execution: {str(e)}")
                retry -= 1
                if retry > 0:
                    logging.info(
                        f"Retrying generate_initial_response_async (Attempt: {4 - retry})"
                    )
                    message = await cls.async_generate_initial_response(message)
                else:
                    message.analysis_result = "Error occurred after several attempts."
                    logging.error("Exceeded maximum retry attempts")
        try:
            message.bot_text = await generate_comprehensive_response_async(
                user_text=message.user_text,
                history=message.history,
                context=message.context,
                analysis_description=message.analysis_description,
                analysis_script=message.analysis_script,
                analysis_result=message.analysis_result,
            )
        except Exception as e:
            logging.error(
                f"Error during generate_comprehensive_response_async: {str(e)}"
            )
            raise RuntimeError(f"Error in async_generate_final_response: {str(e)}")
        return message
