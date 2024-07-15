from pathlib import Path
from tqdm import tqdm
from gradio_client import Client, handle_file


user_message = (
    "You are to assist me in accomplishing a task about the input video. Reply to me with a precise yet detailed response. For how you would succeed in the recaptioning task, read the following Instructions section and Then, make your response with a elaborate paragraph.\n"
    "# Instructions\n"
    "1. Avoid providing over detailed information such as color, counts of any objects as you are terrible regarding observing these details\n"
    "2. Instead, you should carefully go over the provided video and reason about key information about the overall video\n"
    "3. If you are not sure about something, do not include it in you response.\n"
    "# Task\n"
    "Describe the background, characters and the actions in the provided video.\n"
)


class GradioClientPllava:
    def __init__(self):
        url = 'http://127.0.0.1:7868'

        client = Client(url)
        self.predict = client.predict

    # def upload_img(self, fpath_video):
    #     '''
    #     Args:
    #         gr_img
    #         gr_video
    #     Returns:
    #     '''
    #     image, video, textbox = self.predict(
    #         None,
    #         {'video': handle_file(fpath_video)},
    #         api_name="/upload_img",
    #     )

    # def gradio_ask(self):
    #     # user_message = 'Please describe this video by generating dense captions.'

    #     textbox, chatbot = self.predict(
    #         user_message,
    #         api_name="/gradio_ask_1",
    #     )
    #     return chatbot

    # def gradio_answer(self, chatbot):
    #     result = self.predict(
    #         chatbot,
    #         api_name="/gradio_answer",# serialize=False,
    #     )
    #     print(result)
    #     return result

    # def gradio_reset(self):
    #     chatbot, image, video, textbox = self.predict(
    #         api_name="/gradio_reset",
    #     )
    #     return chatbot, image, video, textbox

    # def upload_and_query(self, fpath_video):
    #     chatbot, image, video, textbox = self.gradio_reset()
    #     self.upload_img(fpath_video)
    #     chatbot = self.gradio_ask()
    #     return self.gradio_answer(chatbot)

    def do_one(self, fpath_video: Path):
        # - predict(gr_video, chatbot, user_message, system_string, num_beams, temperature, api_name="/gradio_upload_ask_answer_reset") -> conversation
        #     Parameters:
        #     - [Video] gr_video: Dict(video: filepath, subtitles: filepath | None) (required)
        #     - [Chatbot] chatbot: Tuple[str | Dict(file: filepath, alt_text: str | None) | None, str | Dict(file: filepath, alt_text: str | None) | None] (not required, defaults to:   [])
        #     - [Textbox] user_message: str (required)
        #     - [Textbox] system_string: str (not required, defaults to:   You are Pllava, a large vision-language assistant.
        # You are able to understand the video content that the user provides, and assist the user with a variety of tasks using natural language.
        # Follow the instructions carefully and explain your answers in detail based on the provided video.
        # )
        #     - [Slider] num_beams: float (not required, defaults to:   1)  (numeric value between 1 and 5)
        #     - [Slider] temperature: float (not required, defaults to:   1.0)  (numeric value between 0.1 and 2.0)
        #     Returns:
        #     - [Chatbot] conversation: Tuple[str | Dict(file: filepath, alt_text: str | None) | None, str | Dict(file: filepath, alt_text: str | None) | None]
        return self.predict(
            {'video': handle_file(fpath_video)},
            chatbot=[],
            user_message=user_message,
            api_name="/gradio_upload_ask_answer_reset",
        )[-1][1]


    def do_all(self, dirname):
        results = []
        # upload_and_query = self.upload_and_query
        do_one = self.do_one
        for fpath_video in tqdm(Path(dirname).glob('*.mp4')):
            # result = upload_and_query(fpath_video)
            result = do_one(fpath_video)
            results.append(result)
        return results
