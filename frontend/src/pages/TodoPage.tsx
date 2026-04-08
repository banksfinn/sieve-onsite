import { useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { AppSidebar } from '@/components/common';
import { SlackNotificationChip } from '@/components/notifications';
import { TagBadge, TagSelector } from '@/components/tags';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { DatePicker } from '@/components/ui/date-picker';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '@/components/ui/select';
import {
    useGetTodos,
    useCreateTodo,
    useUpdateTodo,
    useDeleteTodo,
    useCreateTag,
    getGetTodosQueryKey,
    getGetTagsQueryKey,
    Todo,
    TodoCreateRequestRecurrenceType,
} from '@/openapi/fullstackBase';
import { useSnackbar } from '@/store/components/snackbarSlice';
import { Trash2, ChevronDown, Repeat } from 'lucide-react';

export default function TodoPage() {
    const [newTodoTitle, setNewTodoTitle] = useState('');
    const [newTodoDueAt, setNewTodoDueAt] = useState<Date | undefined>(undefined);
    const [newTodoSlackNotification, setNewTodoSlackNotification] = useState(false);
    const [newTodoTimingOverride, setNewTodoTimingOverride] = useState<string[] | null>(null);
    const [newTodoTagIds, setNewTodoTagIds] = useState<number[]>([]);
    const [advancedOpen, setAdvancedOpen] = useState(false);
    const [recurrenceType, setRecurrenceType] = useState<TodoCreateRequestRecurrenceType>(null);
    const [recurrenceRule, setRecurrenceRule] = useState('');
    const [recurrenceStart, setRecurrenceStart] = useState<Date | undefined>(undefined);
    const [recurrenceEnd, setRecurrenceEnd] = useState<Date | undefined>(undefined);
    const queryClient = useQueryClient();
    const { showSuccess, showError } = useSnackbar();

    const { data: todosResponse, isLoading } = useGetTodos();
    const todos = (todosResponse as { entities: Todo[] } | undefined)?.entities ?? [];

    const createTodo = useCreateTodo({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTodosQueryKey() });
                setNewTodoTitle('');
                setNewTodoDueAt(undefined);
                setNewTodoSlackNotification(false);
                setNewTodoTimingOverride(null);
                setNewTodoTagIds([]);
                setRecurrenceType(null);
                setRecurrenceRule('');
                setRecurrenceStart(undefined);
                setRecurrenceEnd(undefined);
                setAdvancedOpen(false);
                showSuccess('Todo created!');
            },
            onError: () => {
                showError('Failed to create todo');
            },
        },
    });

    const createTag = useCreateTag({
        mutation: {
            onSuccess: (data) => {
                queryClient.invalidateQueries({ queryKey: getGetTagsQueryKey() });
                if (data.id) {
                    setNewTodoTagIds((prev) => [...prev, data.id]);
                }
                showSuccess('Tag created!');
            },
            onError: () => {
                showError('Failed to create tag');
            },
        },
    });

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

    const deleteTodo = useDeleteTodo({
        mutation: {
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: getGetTodosQueryKey() });
                showSuccess('Todo deleted!');
            },
            onError: () => {
                showError('Failed to delete todo');
            },
        },
    });

    const handleCreateTodo = (e: React.FormEvent) => {
        e.preventDefault();
        if (!newTodoTitle.trim()) return;
        createTodo.mutate({
            data: {
                title: newTodoTitle.trim(),
                due_at: newTodoDueAt?.toISOString() ?? null,
                slack_notification: newTodoSlackNotification,
                notification_timing_override: newTodoTimingOverride,
                tag_ids: newTodoTagIds.length > 0 ? newTodoTagIds : undefined,
                recurrence_type: recurrenceType,
                recurrence_rule: recurrenceRule || null,
                recurrence_start: recurrenceStart?.toISOString() ?? null,
                recurrence_end: recurrenceEnd?.toISOString() ?? null,
            },
        });
    };

    const handleCreateTagInline = (name: string) => {
        createTag.mutate({
            data: {
                name,
                color: '#3b82f6',
            },
        });
    };

    const handleUpdateDueDate = (todo: Todo, dueAt: Date | undefined) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: {
                id: todo.id,
                due_at: dueAt?.toISOString() ?? null,
                ...(dueAt === undefined && { slack_notification: false }),
            },
        });
    };

    const handleUpdateSlackNotification = (todo: Todo, enabled: boolean) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: {
                id: todo.id,
                slack_notification: enabled,
            },
        });
    };

    const handleUpdateNotificationTiming = (todo: Todo, timing: string[] | null) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: {
                id: todo.id,
                notification_timing_override: timing,
            },
        });
    };

    const handleToggleComplete = (todo: Todo) => {
        updateTodo.mutate({
            todoId: todo.id,
            data: { id: todo.id, completed: !todo.completed },
        });
    };

    const handleDeleteTodo = (todoId: number) => {
        deleteTodo.mutate({ todoId });
    };

    return (
        <AppSidebar>
            <div className="container mx-auto max-w-2xl py-8 px-4">
                <Card>
                    <CardHeader>
                        <CardTitle>Todos</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                        <form onSubmit={handleCreateTodo} className="space-y-3">
                            <div className="flex gap-2">
                                <Input
                                    placeholder="What needs to be done?"
                                    value={newTodoTitle}
                                    onChange={(e) => setNewTodoTitle(e.target.value)}
                                    disabled={createTodo.isPending}
                                />
                                <Button
                                    type="submit"
                                    disabled={createTodo.isPending || !newTodoTitle.trim()}
                                >
                                    Add
                                </Button>
                            </div>
                            <div className="flex gap-2 flex-wrap items-center">
                                <DatePicker
                                    date={newTodoDueAt}
                                    onDateChange={(date) => {
                                        setNewTodoDueAt(date);
                                        if (!date) {
                                            setNewTodoSlackNotification(false);
                                            setNewTodoTimingOverride(null);
                                        }
                                    }}
                                    placeholder="Due date & time"
                                    disabled={createTodo.isPending}
                                    className="w-[240px]"
                                />
                                <SlackNotificationChip
                                    enabled={newTodoSlackNotification}
                                    onEnabledChange={setNewTodoSlackNotification}
                                    timingOverride={newTodoTimingOverride}
                                    onTimingChange={setNewTodoTimingOverride}
                                    disabled={createTodo.isPending || !newTodoDueAt}
                                />
                            </div>

                            <TagSelector
                                selectedTagIds={newTodoTagIds}
                                onChange={setNewTodoTagIds}
                                onCreateTag={handleCreateTagInline}
                                placeholder="Add tags..."
                            />

                            <Collapsible open={advancedOpen} onOpenChange={setAdvancedOpen}>
                                <CollapsibleTrigger asChild>
                                    <Button
                                        variant="ghost"
                                        size="sm"
                                        type="button"
                                        className="flex items-center gap-1 text-muted-foreground"
                                    >
                                        <ChevronDown
                                            className={`h-4 w-4 transition-transform ${
                                                advancedOpen ? 'rotate-180' : ''
                                            }`}
                                        />
                                        Advanced (Recurrence)
                                    </Button>
                                </CollapsibleTrigger>
                                <CollapsibleContent className="space-y-3 pt-2">
                                    <div className="flex gap-2 flex-wrap">
                                        <Select
                                            value={recurrenceType ?? ''}
                                            onValueChange={(value) =>
                                                setRecurrenceType(
                                                    value as TodoCreateRequestRecurrenceType
                                                )
                                            }
                                            disabled={createTodo.isPending}
                                        >
                                            <SelectTrigger className="w-[200px]">
                                                <SelectValue placeholder="Recurrence type" />
                                            </SelectTrigger>
                                            <SelectContent>
                                                <SelectItem value="fixed_schedule">
                                                    Fixed Schedule
                                                </SelectItem>
                                                <SelectItem value="from_completion">
                                                    From Completion
                                                </SelectItem>
                                            </SelectContent>
                                        </Select>
                                        <Input
                                            placeholder="RRule (e.g., FREQ=DAILY)"
                                            value={recurrenceRule}
                                            onChange={(e) => setRecurrenceRule(e.target.value)}
                                            disabled={createTodo.isPending}
                                            className="w-[240px]"
                                        />
                                    </div>
                                    <div className="flex gap-2 flex-wrap">
                                        <DatePicker
                                            date={recurrenceStart}
                                            onDateChange={setRecurrenceStart}
                                            placeholder="Recurrence start"
                                            disabled={createTodo.isPending}
                                            className="w-[240px]"
                                        />
                                        <DatePicker
                                            date={recurrenceEnd}
                                            onDateChange={setRecurrenceEnd}
                                            placeholder="Recurrence end"
                                            disabled={createTodo.isPending}
                                            className="w-[240px]"
                                        />
                                    </div>
                                </CollapsibleContent>
                            </Collapsible>
                        </form>

                        {isLoading ? (
                            <p className="text-muted-foreground text-center py-4">Loading...</p>
                        ) : todos.length === 0 ? (
                            <p className="text-muted-foreground text-center py-4">
                                No todos yet. Add one above!
                            </p>
                        ) : (
                            <ul className="space-y-2">
                                {todos.map((todo) => (
                                    <li
                                        key={todo.id}
                                        className="flex flex-col gap-2 p-3 rounded-lg border bg-card hover:bg-accent/50 transition-colors"
                                    >
                                        <div className="flex items-center gap-3">
                                            <Checkbox
                                                checked={todo.completed}
                                                onCheckedChange={() => handleToggleComplete(todo)}
                                                disabled={updateTodo.isPending}
                                            />
                                            <span
                                                className={`flex-1 flex items-center gap-2 ${
                                                    todo.completed
                                                        ? 'line-through text-muted-foreground'
                                                        : ''
                                                }`}
                                            >
                                                {todo.title}
                                                {todo.recurrence_rule && (
                                                    <span
                                                        className="inline-flex items-center gap-1 text-xs text-muted-foreground"
                                                        title={`${
                                                            todo.recurrence_type ===
                                                            'fixed_schedule'
                                                                ? 'Fixed'
                                                                : 'From completion'
                                                        }: ${todo.recurrence_rule}`}
                                                    >
                                                        <Repeat className="h-3 w-3" />
                                                    </span>
                                                )}
                                            </span>
                                            <Button
                                                variant="ghost"
                                                size="icon"
                                                onClick={() => handleDeleteTodo(todo.id)}
                                                disabled={deleteTodo.isPending}
                                            >
                                                <Trash2 className="h-4 w-4 text-muted-foreground hover:text-destructive" />
                                            </Button>
                                        </div>
                                        {/* Tags display */}
                                        {todo.tags && todo.tags.length > 0 && (
                                            <div className="flex gap-1 ml-7 flex-wrap">
                                                {todo.tags.map((tag) => (
                                                    <TagBadge key={tag.id} tag={tag} />
                                                ))}
                                            </div>
                                        )}
                                        <div className="flex gap-2 ml-7 flex-wrap items-center">
                                            <DatePicker
                                                date={
                                                    todo.due_at ? new Date(todo.due_at) : undefined
                                                }
                                                onDateChange={(date) =>
                                                    handleUpdateDueDate(todo, date)
                                                }
                                                placeholder="Due"
                                                disabled={updateTodo.isPending}
                                                className="h-8 text-xs w-[200px]"
                                            />
                                            <SlackNotificationChip
                                                enabled={todo.slack_notification ?? false}
                                                onEnabledChange={(enabled) =>
                                                    handleUpdateSlackNotification(todo, enabled)
                                                }
                                                timingOverride={
                                                    todo.notification_timing_override ?? null
                                                }
                                                onTimingChange={(timing) =>
                                                    handleUpdateNotificationTiming(todo, timing)
                                                }
                                                disabled={updateTodo.isPending || !todo.due_at}
                                                size="sm"
                                            />
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        )}
                    </CardContent>
                </Card>
            </div>
        </AppSidebar>
    );
}
