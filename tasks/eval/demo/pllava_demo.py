import logging
from argparse import ArgumentParser
import gradio as gr
from tasks.eval.model_utils import load_pllava
from tasks.eval.eval_utils import ChatPllava, conv_templates
from tasks.eval.demo import pllava_theme
logger = logging.getLogger(__name__)


class PLLaVADemo:
    def __init__(self, args):
        chat = init_model(args)
        self.chat_ask = chat.ask
        self.chat_answer = chat.answer
        self.chat_upload_img = chat.upload_img
        self.chat_upload_video = chat.upload_video
        self.INIT_CONVERSATION = conv_templates[args.conv_mode]

    def upload_img(self, gr_img, gr_video, chat_state=None, num_segments=None, img_list=None):
        print(f'gr_img={gr_img}, gr_video={gr_video}, img_list={img_list}')
        chat_state = self.INIT_CONVERSATION.copy() if chat_state is None else chat_state
        img_list = [] if img_list is None else img_list

        if gr_img is None and gr_video is None:
            return None, None, gr.update(interactive=True), gr.update(interactive=True, placeholder='Please upload video/image first!'), chat_state, None
        if gr_video:
            print('upload_img: uploading video to chat model')
            llm_message, img_list, chat_state = self.chat_upload_video(gr_video, chat_state, img_list, num_segments)
            return (
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True, placeholder='Type and press Enter'),
                gr.update(value="Start Chatting", interactive=False),
                chat_state,
                img_list,
            )
        if gr_img:
            print('upload_img: uploading image to chat model')
            llm_message, img_list,chat_state = self.chat_upload_img(gr_img, chat_state, img_list)
            return (
                gr.update(interactive=True),
                gr.update(interactive=True),
                gr.update(interactive=True, placeholder='Type and press Enter'),
                gr.update(value="Start Chatting", interactive=False),
                chat_state,
                img_list
            )

    def gradio_ask(self, user_message, chatbot, chat_state, system):
        print('gradio_ask')
        if len(user_message) == 0:
            return gr.update(interactive=True, placeholder='Input should not be empty!'), chatbot, chat_state
        chat_state = self.chat_ask(user_message, chat_state, system)
        chatbot = chatbot + [[user_message, None]]
        return '', chatbot, chat_state

    def gradio_answer(self, chatbot, chat_state, img_list, num_beams, temperature):
        print('gradio_answer')
        llm_message, llm_message_token, chat_state = self.chat_answer(conv=chat_state, img_list=img_list, max_new_tokens=200, num_beams=num_beams, temperature=temperature)
        llm_message = llm_message.replace("<s>", "") # handle <s>
        chatbot[-1][1] = llm_message
        print(chat_state)
        print(f"Answer: {llm_message}")
        return chatbot, chat_state, img_list

    def gradio_upload_ask_answer_reset(self, gr_video: str, img_list: list, chat_state, chatbot: list, user_message: str, system_string: str, num_beams: float, temperature: float):

        # Upload
        # def upload_img(self, gr_img, gr_video, chat_state=None, num_segments=None, img_list=None):
        # chatbot = None
        # chat_state: Conversation = self.INIT_CONVERSATION.copy()
        # img_list = []

        # if chat_state is not None:
        #     chat_state: Conversation = self.INIT_CONVERSATION.copy()
        # if img_list is not None:
        #     img_list = []
        # assert img_list is not None

        # if chat_state is not None:
        #     logger.warning('gradio_upload_ask_answer_reset: start: chat_state is not None')
        #     chat_state: Conversation = self.INIT_CONVERSATION.copy()
        # else:
            # logger.warning(f'gradio_upload_ask_answer_reset: start: len(chat_state.messages)={len(chat_state.messages)}')
        chat_state = self.INIT_CONVERSATION.copy()

        # if img_list is not None:
        #     # logger.warning('gradio_upload_ask_answer_reset: start: img_list is None')
        #     img_list = []
        # else:
        #     img_list = []
        img_list = []
        # else:
        #     logger.warning(f'gradio_upload_ask_answer_reset: start: len(img_list)={len(img_list)}')

        if not gr_video:
            raise ValueError('upload_img: no video uploaded to chat model')
        llm_message, img_list, chat_state = self.chat_upload_video(gr_video, chat_state, img_list)
        # logger.warning(f'gradio_upload_ask_answer_reset: after upload_video: len(chat_state.messages)={len(chat_state.messages)}')
        # logger.warning(f'gradio_upload_ask_answer_reset: after upload_video: len(img_list)={len(img_list)}')

        # Ask
        # def gradio_ask(self, user_message, chatbot, chat_state, system_string: str):
        # print('gradio_ask')
        if len(user_message) == 0:
            raise ValueError('Input should not be empty!')
        chat_state = self.chat_ask(user_message, chat_state, system_string)
        # logger.warning(f'gradio_upload_ask_answer_reset: after ask: len(chat_state.messages)={len(chat_state.messages)}')
        # logger.warning(f'gradio_upload_ask_answer_reset: after ask: len(img_list)={len(img_list)}')

        chatbot = chatbot + [[user_message, None]]

        # Answer
        # print(f'gradio_answer: img_list={img_list}')
        llm_message, llm_message_token, chat_state = self.chat_answer(conv=chat_state, img_list=img_list, max_new_tokens=200, num_beams=num_beams, temperature=temperature)
        # logger.warning(f'gradio_upload_ask_answer_reset: after answer: len(chat_state.messages)={len(chat_state.messages)}')
        # logger.warning(f'gradio_upload_ask_answer_reset: after answer: len(img_list)={len(img_list)}')

        llm_message = llm_message.replace("<s>", "") # handle <s>
        chatbot[-1][1] = llm_message
        return chatbot, chat_state


    # ========================================
    #             Gradio Setting
    # ========================================
    def gradio_reset(self, chat_state, img_list):
        print('gradio_reset')
        if chat_state is not None:
            chat_state = self.INIT_CONVERSATION.copy()
        if img_list is not None:
            img_list = []
        # clear.click(self.gradio_reset, [chat_state, img_list], [chatbot, up_image, up_video, text_input, upload_button, chat_state, img_list])
        return (
            None,
            gr.update(value=None, interactive=True),
            gr.update(value=None, interactive=True),
            gr.update(placeholder='Please upload your video first', interactive=False),
            gr.update(value="Upload & Start Chat", interactive=True),
            chat_state,
            img_list
        )


    def build_interface(self, args):
        model_description = f"""
            # MODEL INFO
            - pretrained_model_name_or_path:{args.pretrained_model_name_or_path}
            - use_lora:{args.use_lora}
            - weight_dir:{args.weight_dir}
        """
        with gr.Blocks(title="PLLaVA",
                    theme=pllava_theme,
                    css="#chatbot {overflow:auto; height:500px;} #InputVideo {overflow:visible; height:320px;} footer {visibility: none}") as demo:
            gr.Markdown(TITLE)
            gr.Markdown(DESCRIPTION)
            gr.Markdown(model_description)
            with gr.Row():
                with gr.Column(scale=0.5, visible=True) as video_upload:
                    # with gr.Column(elem_id="image", scale=0.5) as img_part:
                    with gr.Tab("Video", elem_id='video_tab'):
                        up_video = gr.Video(interactive=True, include_audio=True, elem_id="video_upload", height=360)
                        # up_video = gr.Video(include_audio=True, elem_id="video_upload", height=360)
                    with gr.Tab("Image", elem_id='image_tab'):
                        up_image = gr.Image(type="pil", interactive=True, elem_id="image_upload", height=360)
                    upload_button = gr.Button(value="Upload & Start Chat", interactive=True, variant="primary")
                    clear = gr.Button("Restart")

                    # num_segments = gr.Slider(
                    #     minimum=8,
                    #     maximum=64,
                    #     value=8,
                    #     step=1,
                    #     interactive=True,
                    #     label="Video Segments",
                    # )

                with gr.Column(visible=True) as input_raws:
                    system_string = gr.Textbox(SYSTEM, interactive=True, label='system')
                    num_beams = gr.Slider(
                        minimum=1,
                        maximum=5,
                        value=1,
                        step=1,
                        interactive=True,
                        label="beam search numbers",
                    )
                    temperature = gr.Slider(
                        minimum=0.1,
                        maximum=2.0,
                        value=1.0,
                        step=0.1,
                        interactive=True,
                        label="Temperature",
                    )

                    chat_state = gr.State()
                    img_list = gr.State()
                    chatbot = gr.Chatbot(elem_id="chatbot", label='Conversation')
                    with gr.Row():
                        with gr.Column(scale=0.7):
                            text_input = gr.Textbox(show_label=False, placeholder='Please upload your video first', interactive=False, container=False)
                        with gr.Column(scale=0.15, min_width=0):
                            run = gr.Button("💭Send")
                        with gr.Column(scale=0.15, min_width=0):
                            clear = gr.Button("🔄Clear")
                        with gr.Column(scale=0.7):
                            infer = gr.Textbox(show_label=False, placeholder='test', interactive=False, container=False)

            with gr.Row():
                examples = gr.Examples(
                    examples=[
                        ['example/jesse_dance.mp4', 'What is the man doing?'],
                        ['example/yoga.mp4', 'What is the woman doing?'],
                        ['example/cooking.mp4', 'Describe the background, characters and the actions in the provided video.'],
                        # ['example/cooking.mp4', 'What is happening in the video?'],
                        ['example/working.mp4', 'Describe the background, characters and the actions in the provided video.'],
                        ['example/1917.mov', 'Describe the background, characters and the actions in the provided video.'],
                    ],
                    inputs=[up_video, text_input]
                )


            # chat = init_model(args)

            upload_button.click(
                fn=self.upload_img,
                inputs=[up_image, up_video, chat_state],
                outputs=[up_image, up_video, text_input, upload_button, chat_state, img_list]
            )

            text_input.submit(self.gradio_ask, [text_input, chatbot, chat_state, system_string], [text_input, chatbot, chat_state]).then(
                self.gradio_answer, [chatbot, chat_state, img_list, num_beams, temperature], [chatbot, chat_state, img_list]
            )
            run.click(self.gradio_ask, [text_input, chatbot, chat_state, system_string], [text_input, chatbot, chat_state]).then(
                self.gradio_answer, [chatbot, chat_state, img_list, num_beams, temperature], [chatbot, chat_state, img_list]
            )
            run.click(lambda: "", None, text_input)
            # clear.click(self.gradio_reset, [chat_state, img_list], [chatbot, up_image, up_video, text_input, upload_button, chat_state, img_list], queue=False)
            clear.click(self.gradio_reset, [chat_state, img_list], [chatbot, up_image, up_video, text_input, upload_button, chat_state, img_list])

            # def gradio_upload_ask_answer_reset(self, gr_video: str, chatbot: Chatbot, chat_state: Conversation=None, num_segments=None, img_list=None):
            infer.submit(self.gradio_upload_ask_answer_reset, [up_video, img_list, chat_state, chatbot, text_input, system_string, num_beams, temperature], [chatbot, chat_state])

            # Interface(fn=self.gradio_upload_ask_answer_reset, inputs=[up_video, chatbot, text_input, system_string, num_beams, temperature], outputs=None)#, outputs=[chatbot])
            # infer.click(
            #     fn=self.upload_img,
            #     inputs=[up_image, up_video, chat_state],
            #     outputs=[up_image, up_video, text_input, upload_button, chat_state, img_list]
            # ).then(self.gradio_ask, [text_input, chatbot, chat_state, system_string], [text_input, chatbot, chat_state]).then(
            #     self.gradio_answer, [chatbot, chat_state, img_list, num_beams, temperature], [chatbot, chat_state, img_list]
            # )
        # demo.queue(max_size=5)
        return demo
        # print('launching demo')

        # demo.launch(share=True, server_port=args.server_port, debug=True, show_error=True)
        # demo.launch(server_name="0.0.0.0", server_port=10034, enable_queue=True)


SYSTEM="""You are Pllava, a large vision-language assistant.
You are able to understand the video content that the user provides, and assist the user with a variety of tasks using natural language.
Follow the instructions carefully and explain your answers in detail based on the provided video.
"""
# INIT_CONVERSATION: Conversation = conv_plain_v1.copy()


TITLE = """<h1 align="center"><a href="https://github.com/magic-research/PLLaVA"><img src="https://raw.githubusercontent.com/magic-research/PLLaVA/main/assert/logo.png" alt="PLLAVA" border="0" style="margin: 0 auto; height: 100px;" /></a> </h1>"""
DESCRIPTION = (
    """<br><p><a href='https://github.com/magic-research/PLLaVA'>
    # PLLAVA!
    <img src='https://img.shields.io/badge/Github-Code-blue'></a></p><p>
    - Upload A Video
    - Press Upload
    - Start Chatting
    """
)


# ========================================
#             Model Initialization
# ========================================
def init_model(args):
    print('Initializing PLLaVA')
    model, processor = load_pllava(
        args.pretrained_model_name_or_path, args.num_frames,
        use_lora=args.use_lora,
        weight_dir=args.weight_dir,
        lora_alpha=args.lora_alpha,
        use_multi_gpus=args.use_multi_gpus)
    # if not args.use_multi_gpus:
    #     model = model.to('cuda', non_blocking=True)
    return ChatPllava(model, processor)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "--pretrained_model_name_or_path",
        type=str,
        required=True,
        # default='llava-hf/llava-1.5-7b-hf'
    )
    parser.add_argument(
        "--num_frames",
        type=int,
        required=True,
        default=4,
    )
    parser.add_argument(
        "--use_lora",
        action='store_true'
    )
    parser.add_argument(
        "--use_multi_gpus",
        action='store_true'
    )
    parser.add_argument(
        "--weight_dir",
        type=str,
        required=False,
        default=None,
    )
    parser.add_argument(
        "--conv_mode",
        type=str,
        required=False,
        default=None,
    )
    parser.add_argument(
        "--lora_alpha",
        type=int,
        required=False,
        default=None,
    )
    parser.add_argument(
        "--server_port",
        type=int,
        required=False,
        default=7868,
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    pllava_demo = PLLaVADemo(args)
    demo = pllava_demo.build_interface(args)
    logger.warn('launching demo')
    demo.queue()
    demo.launch(server_name="0.0.0.0", share=True, server_port=args.server_port, debug=True, show_error=True, quiet=False, show_api=True)
    # demo.launch(server_name="0.0.0.0", share=True, server_port=args.server_port, debug=False, show_error=True, quiet=False, show_api=True)
    # demo.launch(share=True)
