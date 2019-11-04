import datetime
import time
from .renderer.textmessage import LiveChatTextMessageRenderer
from .renderer.paidmessage import LiveChatPaidMessageRenderer
from .renderer.paidsticker import LiveChatPaidStickerRenderer
from .renderer.legacypaid import LiveChatLegacyPaidMessageRenderer
from ... import mylogger
from ... import config
logger = mylogger.get_logger(__name__,mode=config.LOGGER_MODE)

class CompatibleProcessor:

    def process(self, chat_components: list):

        chatlist = []
        timeout = 0
        ret={}
        ret["kind"] = "youtube#liveChatMessageListResponse"
        ret["etag"] = ""
        ret["nextPageToken"] = ""

        if chat_components:
            for chat_component in chat_components:
                timeout += chat_component.get('timeout', 0)
                chatdata = chat_component.get('chatdata')
             
                if chatdata is None: break
                for action in chatdata:
                    if action is None: continue
                    if action.get('addChatItemAction') is None: continue
                    if action['addChatItemAction'].get('item') is None: continue

                    chat = self.parse(action)
                    if chat:
                        chatlist.append(chat)
        ret["pollingIntervalMillis"] = int(timeout*1000)
        ret["pageInfo"]={
            "totalResults":len(chatlist),
            "resultsPerPage":len(chatlist),
        }
        ret["items"] = chatlist

        return ret

    def parse(self, sitem):

        action = sitem.get("addChatItemAction")
        if action:
            item = action.get("item")
        if item is None: return None
        rd={}
        try:
            renderer = self.get_renderer(item)
            if renderer == None:
                return None

            rd["kind"] = "youtube#liveChatMessage"
            rd["etag"] = ""
            rd["id"] = 'LCC.' + renderer.get_id()
            rd["snippet"]       = renderer.get_snippet()
            rd["authorDetails"] = renderer.get_authordetails()
        except (KeyError,TypeError,AttributeError) as e:
            logger.error(f"Error: {str(type(e))}-{str(e)}")
            logger.error(f"item: {sitem}")
            return None
        
        return rd        

    def get_renderer(self, item):
        if item.get("liveChatTextMessageRenderer"):
            renderer = LiveChatTextMessageRenderer(item)
        elif item.get("liveChatPaidMessageRenderer"):
            renderer = LiveChatPaidMessageRenderer(item)
        elif item.get( "liveChatPaidStickerRenderer"):
            renderer = LiveChatPaidStickerRenderer(item)
        elif item.get("liveChatLegacyPaidMessageRenderer"):
            renderer = LiveChatLegacyPaidMessageRenderer(item)
        else:
            renderer = None
        return renderer

