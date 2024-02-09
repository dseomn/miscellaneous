/*
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     https://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

use std::collections;
use std::sync;

pub struct Queue<T: Sized> {
    data: sync::Arc<(sync::Mutex<collections::VecDeque<T>>, sync::Condvar)>,
}

impl<T> Clone for Queue<T> {
    fn clone(&self) -> Self {
        Queue { data: self.data.clone() }
    }
}

impl<T> Queue<T> {
    pub fn new() -> Queue<T> {
        Queue {
            data: sync::Arc::new(
                (sync::Mutex::new(collections::VecDeque::new()), sync::Condvar::new())
            ),
        }
    }

    pub fn push(&mut self, item: T) {
        let (mutex, condition) = &*self.data;
        let mut mutex_guard = mutex.lock().unwrap();
        (*mutex_guard).push_back(item);
        condition.notify_one();
    }

    pub fn pop(&mut self) -> T {
        // TODO: Can this be simplified?
        loop {
            let (mutex, condition) = &*self.data;
            let mut mutex_guard = mutex.lock().unwrap();
            if let Some(item) = (*mutex_guard).pop_front() {
                return item;
            }
            let mut condition_guard = condition.wait(mutex_guard).unwrap();
            if let Some(item) = (*condition_guard).pop_front() {
                return item;
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn push_pop() {
        let mut queue = Queue::<u32>::new();
        queue.push(42);
        let result = queue.pop();
        assert_eq!(result, 42);
    }
}
