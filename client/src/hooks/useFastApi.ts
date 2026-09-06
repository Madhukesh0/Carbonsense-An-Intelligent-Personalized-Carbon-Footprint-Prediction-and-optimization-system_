import { type QueryKey, useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { fastApiRequest } from "@/lib/fastapiClient";

export function useFastApiQuery<T>(key: QueryKey, path: string, enabled = true) {
  return useQuery<T>({ queryKey: key, queryFn: () => fastApiRequest<T>(path), enabled });
}

export function useFastApiMutation<TResponse, TInput>(path: string, method: "POST" | "PATCH" | "PUT" | "DELETE" = "POST", invalidate: QueryKey[] = []) {
  const queryClient = useQueryClient();
  return useMutation<TResponse, Error, TInput>({
    mutationFn: input => fastApiRequest<TResponse>(path, { method, body: input }),
    onSuccess: async () => { await Promise.all(invalidate.map(key => queryClient.invalidateQueries({ queryKey: key }))); },
  });
}
