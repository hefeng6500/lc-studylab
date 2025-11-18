"use client";

import { useState } from "react";
import {
  Brain,
  PanelLeft,
  PenSquare,
  Search,
  Library,
  UserRound,
} from "lucide-react";
import { ChatEnhanced } from "@/components/chat/chat-enhanced";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export default function ChatUIPage() {
  const [selectedChat, setSelectedChat] = useState<string | null>(
    "系统指令解读"
  );
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isScrolled, setIsScrolled] = useState(false);

  const history = [
    "系统指令解读",
    "节气挑战页面设计",
    "设计海报挑战",
    "Node.js 快速搭建API",
    "使用WSL启动前端",
    "Claude Code 安装问题",
    "Guardrails v1 解读",
    "外接RTX5090显卡设置",
    "Compliment exchange",
    "创建 GitHub tag",
    "东西方设计哲学比较",
    "东西方设计哲学对比",
    "东西方设计哲学对比",
    "东西方设计哲学对比",
  ];

  const menuItems = [
    { icon: PenSquare, label: "新聊天" },
    { icon: Search, label: "搜索聊天" },
    { icon: Library, label: "库" },
  ];

  const handleScrollChange = (scrolled: boolean) => {
    console.log("Scroll state changed:", scrolled);
    setIsScrolled(scrolled);
  };

  return (
    <div className="flex h-screen font-sans">
      {/* Sidebar */}
      <aside
        className={`h-screen bg-[#f9f9f9] border-r border-zinc-200 flex flex-col overflow-hidden transition-all duration-300 ease-in-out ${
          sidebarOpen ? "w-[260px]" : "w-[52px]"
        }`}
      >
        {/* Top Section */}
        <div className="flex-shrink-0">
          {/* Header */}
          <div
            className={`flex items-center ${
              sidebarOpen ? "justify-between px-4" : "justify-center"
            } py-3 group relative`}
          >
            {sidebarOpen ? (
              <>
                <div className="flex items-center gap-2">
                  <Brain className="w-6 h-6 text-zinc-700" />
                  <span className="text-lg font-semibold text-zinc-800">
                    ChatGPT
                  </span>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="p-1.5 rounded-md hover:bg-zinc-200 transition-colors"
                >
                  <PanelLeft className="w-5 h-5 text-zinc-600" />
                </button>
              </>
            ) : (
              <>
                <Brain className="w-6 h-6 text-zinc-700 cursor-pointer" />
                {/* Hover overlay with open button */}
                <div
                  className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-zinc-100/80 cursor-pointer"
                  onClick={() => setSidebarOpen(true)}
                >
                  <PanelLeft className="w-5 h-5 text-zinc-600" />
                </div>
              </>
            )}
          </div>

          {/* Menu Items */}
          <div className={`${sidebarOpen ? "px-3" : "px-2"} py-2 space-y-1`}>
            {menuItems.map((item, index) => (
              <button
                key={index}
                className={`w-full flex items-center ${
                  sidebarOpen ? "gap-3 px-3" : "justify-center"
                } h-10 rounded-md hover:bg-zinc-100 transition-colors group`}
              >
                <item.icon className="w-5 h-5 text-zinc-600 group-hover:scale-105 transition-transform" />
                {sidebarOpen && (
                  <span className="text-sm font-medium text-zinc-800">
                    {item.label}
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        {/* Chat History List or Spacer */}
        {sidebarOpen ? (
          <div className="flex-1 overflow-y-auto scrollbar-hide px-3 py-2">
            <div className="space-y-0.5">
              {history.map((chat, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedChat(chat)}
                  className={`w-full text-left px-4 py-1 rounded-md transition-colors truncate text-[15px] leading-8 ${
                    selectedChat === chat
                      ? "bg-zinc-100 text-zinc-900"
                      : "text-zinc-700 hover:bg-zinc-100"
                  }`}
                >
                  {chat}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex-1" />
        )}

        {/* User Info */}
        <div
          className={`flex-shrink-0 p-3 border-t border-zinc-200 flex items-center ${
            sidebarOpen ? "gap-3" : "justify-center"
          }`}
        >
          <Avatar className="w-8 h-8">
            <AvatarFallback className="bg-zinc-300 text-zinc-700">
              <UserRound className="w-4 h-4" />
            </AvatarFallback>
          </Avatar>
          {sidebarOpen && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-zinc-900 truncate">
                feng he
              </div>
              <div className="text-xs text-zinc-500">Plus</div>
            </div>
          )}
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        {/* Top Bar with dynamic shadow */}
        <div
          className="flex-shrink-0 h-[52px] flex items-center justify-center transition-shadow duration-200 bg-white"
          style={{
            boxShadow: isScrolled ? "0 1px 0 #0000000d" : "0 1px 0 transparent",
          }}
        >
          {/* Debug info */}
          <div className="text-xs text-gray-500">
            isScrolled: {isScrolled ? "true" : "false"}
          </div>
        </div>

        {/* Scrollable Content Area */}
        <div className="flex-1 overflow-hidden flex justify-center">
          <ChatEnhanced
            mode="default"
            useTools={true}
            onScrollChange={handleScrollChange}
          />
        </div>
      </main>
    </div>
  );
}
