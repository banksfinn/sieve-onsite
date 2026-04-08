import { useState, useRef, useEffect } from 'react';
import { AppSidebar } from '@/components/common';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getUserTimezone } from '@/components/ui/date-picker';
import { useChat } from '@/openapi/fullstackBase';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { Send, Bot, User, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

export default function ChatPage() {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [conversationId, setConversationId] = useState<string | undefined>(undefined);
    const scrollAreaRef = useRef<HTMLDivElement>(null);
    const inputRef = useRef<HTMLTextAreaElement>(null);
    const { showError } = useSnackbar();

    const chatMutation = useChat({
        mutation: {
            onSuccess: (data) => {
                setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
                setConversationId(data.conversation_id);
            },
            onError: () => {
                showError('Failed to send message');
            },
        },
    });

    // Scroll to bottom when messages change
    useEffect(() => {
        if (scrollAreaRef.current) {
            const scrollContainer = scrollAreaRef.current.querySelector(
                '[data-radix-scroll-area-viewport]'
            );
            if (scrollContainer) {
                scrollContainer.scrollTop = scrollContainer.scrollHeight;
            }
        }
    }, [messages]);

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || chatMutation.isPending) return;

        const userMessage = input.trim();
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        setInput('');

        chatMutation.mutate({
            data: {
                message: userMessage,
                conversation_id: conversationId,
                timezone: getUserTimezone(),
            },
        });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-3xl h-[calc(100vh-8rem)] py-4 px-4 flex flex-col">
                <Card className="flex-1 flex flex-col min-h-0">
                    <CardHeader className="pb-3">
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5" />
                            Todo Assistant
                        </CardTitle>
                        <p className="text-sm text-muted-foreground">
                            Ask me to manage your todos. Try &quot;Show my todos&quot; or
                            &quot;Create a todo to buy groceries due tomorrow&quot;
                        </p>
                    </CardHeader>
                    <CardContent className="flex-1 flex flex-col min-h-0 pb-4">
                        <ScrollArea ref={scrollAreaRef} className="flex-1 pr-4">
                            {messages.length === 0 ? (
                                <div className="flex items-center justify-center h-full text-muted-foreground">
                                    <p>Start a conversation to manage your todos</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {messages.map((message, index) => (
                                        <div
                                            key={index}
                                            className={cn(
                                                'flex gap-3 p-3 rounded-lg',
                                                message.role === 'user'
                                                    ? 'bg-primary/10 ml-8'
                                                    : 'bg-muted mr-8'
                                            )}
                                        >
                                            <div className="flex-shrink-0">
                                                {message.role === 'user' ? (
                                                    <User className="h-5 w-5 text-primary" />
                                                ) : (
                                                    <Bot className="h-5 w-5 text-muted-foreground" />
                                                )}
                                            </div>
                                            <div className="flex-1 whitespace-pre-wrap text-sm">
                                                {message.content}
                                            </div>
                                        </div>
                                    ))}
                                    {chatMutation.isPending && (
                                        <div className="flex gap-3 p-3 rounded-lg bg-muted mr-8">
                                            <Bot className="h-5 w-5 text-muted-foreground flex-shrink-0" />
                                            <div className="flex items-center gap-2 text-sm text-muted-foreground">
                                                <Loader2 className="h-4 w-4 animate-spin" />
                                                Thinking...
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </ScrollArea>

                        <form
                            onSubmit={handleSubmit}
                            className="flex gap-2 mt-4 pt-4 border-t items-end"
                        >
                            <Textarea
                                ref={inputRef}
                                placeholder="Ask about your todos..."
                                value={input}
                                onChange={(e) => setInput(e.target.value)}
                                onKeyDown={handleKeyDown}
                                disabled={chatMutation.isPending}
                                className="flex-1 min-h-[40px] max-h-[200px] resize-none"
                                rows={1}
                            />
                            <Button
                                type="submit"
                                disabled={chatMutation.isPending || !input.trim()}
                                size="icon"
                            >
                                {chatMutation.isPending ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                            </Button>
                        </form>
                    </CardContent>
                </Card>
            </div>
        </AppSidebar>
    );
}
