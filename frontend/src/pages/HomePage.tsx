import { useState, useRef, useEffect, useMemo } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { SlackNotificationChip } from '@/components/notifications';
import { TagChip } from '@/components/tags';
import { Button } from '@/components/ui/button';
import { Checkbox } from '@/components/ui/checkbox';
import { getUserTimezone } from '@/components/ui/date-picker';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
    useGetTodos,
    useUpdateTodo,
    useChat,
    getGetTodosQueryKey,
    Todo,
} from '@/openapi/fullstackBase';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { MessageCircle, X, Send, Bot, User, Loader2, Calendar, Eye, EyeOff } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Message {
    role: 'user' | 'assistant';
    content: string;
}

/**
 * Format a time for display (e.g., "8 PM", "10:30 AM").
 * Only shows minutes if non-zero.
 */
function formatTime(date: Date): string {
    const hours = date.getHours();
    const minutes = date.getMinutes();
    const period = hours >= 12 ? 'PM' : 'AM';
    const hour12 = hours === 0 ? 12 : hours > 12 ? hours - 12 : hours;

    if (minutes === 0) {
        return `${hour12} ${period}`;
    }
    return `${hour12}:${minutes.toString().padStart(2, '0')} ${period}`;
}

/**
 * Format a due date for display.
 * - Today/Tomorrow: show day and time (e.g., "Today at 8 PM")
 * - Within 2 days: show day and time (e.g., "Saturday at 8 PM")
 * - More than 2 days out: show just the day (e.g., "Saturday")
 * - Beyond a week: show date (e.g., "Jan 15")
 */
function formatDueDate(dueAt: string): string {
    const due = new Date(dueAt);
    const now = new Date();
    const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    const dueDate = new Date(due.getFullYear(), due.getMonth(), due.getDate());
    const diffDays = Math.floor((dueDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

    const time = formatTime(due);
    const dayName = due.toLocaleDateString('en-US', { weekday: 'long' });

    if (diffDays < 0) {
        return `Overdue (${due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })})`;
    } else if (diffDays === 0) {
        return `Today at ${time}`;
    } else if (diffDays === 1) {
        return `Tomorrow at ${time}`;
    } else if (diffDays === 2) {
        return `${dayName} at ${time}`;
    } else if (diffDays < 7) {
        return dayName;
    } else {
        return due.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
}

/**
 * Check if a due date is in the future (more than a week out).
 */
function isFutureTodo(dueAt: string | null | undefined): boolean {
    if (!dueAt) return false;
    const due = new Date(dueAt);
    const now = new Date();
    const oneWeekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    return due > oneWeekFromNow;
}

export default function HomePage() {
    const [showFuture, setShowFuture] = useState(false);
    const [showCompleted, setShowCompleted] = useState(false);
    const [chatOpen, setChatOpen] = useState(false);
    const [messages, setMessages] = useState<Message[]>([]);
    const [chatInput, setChatInput] = useState('');
    const [conversationId, setConversationId] = useState<string | undefined>(undefined);

    const queryClient = useQueryClient();
    const { showError } = useSnackbar();
    const scrollAreaRef = useRef<HTMLDivElement>(null);
    const chatInputRef = useRef<HTMLTextAreaElement>(null);

    const { data: todosResponse, isLoading } = useGetTodos();
    const todos = (todosResponse as { entities: Todo[] } | undefined)?.entities ?? [];

    const updateTodo = useUpdateTodo({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTodosQueryKey() });
            },
            onError: () => {
                showError('Failed to update todo');
            },
        },
    });

    const chatMutation = useChat({
        mutation: {
            onSuccess: (data) => {
                setMessages((prev) => [...prev, { role: 'assistant', content: data.response }]);
                setConversationId(data.conversation_id);
                // Refresh todos in case the chat created/modified any
                queryClient.invalidateQueries({ queryKey: getGetTodosQueryKey() });
            },
            onError: () => {
                showError('Failed to send message');
            },
        },
    });

    // Filter todos based on current view settings
    const { currentTodos, futureTodos, completedTodos } = useMemo(() => {
        const current: Todo[] = [];
        const future: Todo[] = [];
        const completed: Todo[] = [];

        for (const todo of todos) {
            if (todo.completed) {
                completed.push(todo);
            } else if (isFutureTodo(todo.due_at)) {
                future.push(todo);
            } else {
                // No due date OR due within a week (including overdue)
                current.push(todo);
            }
        }

        // Sort current todos: overdue first, then by due date, then no due date last
        current.sort((a, b) => {
            if (!a.due_at && !b.due_at) return 0;
            if (!a.due_at) return 1;
            if (!b.due_at) return -1;
            return new Date(a.due_at).getTime() - new Date(b.due_at).getTime();
        });

        // Sort future by due date
        future.sort((a, b) => {
            if (!a.due_at || !b.due_at) return 0;
            return new Date(a.due_at).getTime() - new Date(b.due_at).getTime();
        });

        // Sort completed by most recently updated
        completed.sort(
            (a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        );

        return { currentTodos: current, futureTodos: future, completedTodos: completed };
    }, [todos]);

    // Scroll chat to bottom when messages change
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

    // Focus chat input when chat opens
    useEffect(() => {
        if (chatOpen) {
            setTimeout(() => chatInputRef.current?.focus(), 100);
        }
    }, [chatOpen]);

    const handleToggleComplete = (todo: Todo) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: { id: todo.id, completed: !todo.completed },
        });
    };

    const handleUpdateSlackNotification = (todo: Todo, enabled: boolean) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: { id: todo.id, slack_notification: enabled },
        });
    };

    const handleUpdateNotificationTiming = (todo: Todo, timing: string[] | null) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: { id: todo.id, notification_timing_override: timing },
        });
    };

    const handleChatSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!chatInput.trim() || chatMutation.isPending) return;

        const userMessage = chatInput.trim();
        setMessages((prev) => [...prev, { role: 'user', content: userMessage }]);
        setChatInput('');

        chatMutation.mutate({
            data: {
                message: userMessage,
                conversation_id: conversationId,
                timezone: getUserTimezone(),
            },
        });
    };

    const handleChatKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleChatSubmit(e);
        }
    };

    const renderTodoItem = (todo: Todo) => (
        <li
            key={todo.id}
            className={cn(
                'flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors',
                todo.completed && 'opacity-60'
            )}
        >
            <Checkbox
                checked={todo.completed}
                onCheckedChange={() => handleToggleComplete(todo)}
                disabled={updateTodo.isPending}
                className="mt-0.5"
            />
            <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                    <span
                        className={cn(
                            'flex-1',
                            todo.completed && 'line-through text-muted-foreground'
                        )}
                    >
                        {todo.title}
                    </span>
                    {todo.due_at && !todo.completed && (
                        <>
                            <span
                                className={cn(
                                    'flex items-center gap-1 text-xs flex-shrink-0',
                                    new Date(todo.due_at) < new Date()
                                        ? 'text-destructive'
                                        : 'text-muted-foreground'
                                )}
                            >
                                <Calendar className="h-3 w-3" />
                                {formatDueDate(todo.due_at)}
                            </span>
                            <SlackNotificationChip
                                enabled={todo.slack_notification ?? false}
                                onEnabledChange={(enabled) =>
                                    handleUpdateSlackNotification(todo, enabled)
                                }
                                timingOverride={todo.notification_timing_override ?? null}
                                onTimingChange={(timing) =>
                                    handleUpdateNotificationTiming(todo, timing)
                                }
                                disabled={updateTodo.isPending}
                                size="sm"
                            />
                        </>
                    )}
                </div>
                {todo.tags && todo.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mt-1">
                        {todo.tags.map((tag) => (
                            <TagChip key={tag.id} tag={tag} />
                        ))}
                    </div>
                )}
            </div>
        </li>
    );

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-2xl py-8 px-4">
                <h1 className="text-2xl font-bold mb-6">Home</h1>

                {/* Toggle buttons */}
                <div className="flex gap-2 mb-4">
                    <Button
                        variant={showFuture ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setShowFuture(!showFuture)}
                        className="flex items-center gap-2"
                    >
                        {showFuture ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                        Future ({futureTodos.length})
                    </Button>
                    <Button
                        variant={showCompleted ? 'default' : 'outline'}
                        size="sm"
                        onClick={() => setShowCompleted(!showCompleted)}
                        className="flex items-center gap-2"
                    >
                        {showCompleted ? (
                            <EyeOff className="h-4 w-4" />
                        ) : (
                            <Eye className="h-4 w-4" />
                        )}
                        Completed ({completedTodos.length})
                    </Button>
                </div>

                {/* Main todo list */}
                {isLoading ? (
                    <p className="text-muted-foreground text-center py-8">Loading...</p>
                ) : currentTodos.length === 0 && !showFuture && !showCompleted ? (
                    <div className="text-center py-8">
                        <p className="text-muted-foreground mb-2">No upcoming tasks!</p>
                        <p className="text-sm text-muted-foreground">
                            Use the chat bubble to add new todos
                        </p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {/* Current/Upcoming todos */}
                        {currentTodos.length > 0 && (
                            <div>
                                <h2 className="text-sm font-medium text-muted-foreground mb-2">
                                    Upcoming
                                </h2>
                                <ul className="space-y-2">{currentTodos.map(renderTodoItem)}</ul>
                            </div>
                        )}

                        {/* Future todos */}
                        {showFuture && futureTodos.length > 0 && (
                            <div>
                                <h2 className="text-sm font-medium text-muted-foreground mb-2">
                                    Future
                                </h2>
                                <ul className="space-y-2">{futureTodos.map(renderTodoItem)}</ul>
                            </div>
                        )}

                        {/* Completed todos */}
                        {showCompleted && completedTodos.length > 0 && (
                            <div>
                                <h2 className="text-sm font-medium text-muted-foreground mb-2">
                                    Completed
                                </h2>
                                <ul className="space-y-2">{completedTodos.map(renderTodoItem)}</ul>
                            </div>
                        )}
                    </div>
                )}
            </div>

            {/* Chat bubble */}
            <div className="fixed bottom-6 right-6 z-50">
                {chatOpen ? (
                    <div className="w-96 h-[500px] bg-card border rounded-lg shadow-lg flex flex-col">
                        {/* Chat header */}
                        <div className="flex items-center justify-between p-3 border-b">
                            <div className="flex items-center gap-2">
                                <Bot className="h-5 w-5" />
                                <span className="font-medium">Todo Assistant</span>
                            </div>
                            <Button variant="ghost" size="icon" onClick={() => setChatOpen(false)}>
                                <X className="h-4 w-4" />
                            </Button>
                        </div>

                        {/* Chat messages */}
                        <ScrollArea ref={scrollAreaRef} className="flex-1 p-3">
                            {messages.length === 0 ? (
                                <div className="flex items-center justify-center h-full text-muted-foreground text-sm text-center p-4">
                                    <p>
                                        Ask me to manage your todos!
                                        <br />
                                        Try "Add a todo to buy groceries"
                                    </p>
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {messages.map((message, index) => (
                                        <div
                                            key={index}
                                            className={cn(
                                                'flex gap-2 p-2 rounded-lg text-sm',
                                                message.role === 'user'
                                                    ? 'bg-primary/10 ml-6'
                                                    : 'bg-muted mr-6'
                                            )}
                                        >
                                            <div className="flex-shrink-0">
                                                {message.role === 'user' ? (
                                                    <User className="h-4 w-4 text-primary" />
                                                ) : (
                                                    <Bot className="h-4 w-4 text-muted-foreground" />
                                                )}
                                            </div>
                                            <div className="flex-1 whitespace-pre-wrap">
                                                {message.content}
                                            </div>
                                        </div>
                                    ))}
                                    {chatMutation.isPending && (
                                        <div className="flex gap-2 p-2 rounded-lg bg-muted mr-6 text-sm">
                                            <Bot className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                                            <div className="flex items-center gap-2 text-muted-foreground">
                                                <Loader2 className="h-3 w-3 animate-spin" />
                                                Thinking...
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}
                        </ScrollArea>

                        {/* Chat input */}
                        <form
                            onSubmit={handleChatSubmit}
                            className="flex gap-2 p-3 border-t items-end"
                        >
                            <Textarea
                                ref={chatInputRef}
                                placeholder="Ask about your todos..."
                                value={chatInput}
                                onChange={(e) => setChatInput(e.target.value)}
                                onKeyDown={handleChatKeyDown}
                                disabled={chatMutation.isPending}
                                className="flex-1 min-h-[36px] max-h-[100px] resize-none text-sm"
                                rows={1}
                            />
                            <Button
                                type="submit"
                                disabled={chatMutation.isPending || !chatInput.trim()}
                                size="icon"
                                className="h-9 w-9"
                            >
                                {chatMutation.isPending ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Send className="h-4 w-4" />
                                )}
                            </Button>
                        </form>
                    </div>
                ) : (
                    <Button
                        size="icon"
                        className="h-14 w-14 rounded-full shadow-lg"
                        onClick={() => setChatOpen(true)}
                    >
                        <MessageCircle className="h-6 w-6" />
                    </Button>
                )}
            </div>
        </AppSidebar>
    );
}
