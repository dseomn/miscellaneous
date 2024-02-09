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

use std::thread;

mod queue;

type Callback = dyn FnOnce() + Send;

pub struct ThreadPool {
    workers: Vec<thread::JoinHandle<()>>,
    queue: queue::Queue<Box<Callback>>,
}

impl ThreadPool {
    pub fn new(worker_count: usize) -> ThreadPool {
        let mut pool = ThreadPool {
            workers: vec![],
            queue: queue::Queue::new(),
        };
        for _ in 0..worker_count {
            let mut queue_clone = pool.queue.clone();
            pool.workers.push(thread::spawn(move || {
                loop {
                    queue_clone.pop()();
                }
            }));
        }
        pool
    }

    pub fn run(&mut self, f: Box<Callback>) {
        self.queue.push(f);
    }
}

// TODO: Add a way to close the pool and stop its worker threads.

#[cfg(test)]
mod tests {
    use std::sync::mpsc;

    use super::*;

    #[test]
    fn run() {
        let (tx, rx) = mpsc::channel::<u32>();
        let mut pool = ThreadPool::new(2);
        for i in 0..42 {
            let tx_clone = tx.clone();
            pool.run(Box::new(move || { tx_clone.send(i).unwrap(); }));
        }
        let mut result = (0..42).map(|_| rx.recv().unwrap()).collect::<Vec<_>>();
        result.sort();
        assert_eq!(result, Vec::from_iter(0..42));
    }
}
