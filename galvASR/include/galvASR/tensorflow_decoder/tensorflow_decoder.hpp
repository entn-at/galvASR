// Copyright 2017 Daniel Galvez

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

// http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <cstdint>

#include "itf/decode-itf.h"

namespace galvASR {
    class TensorFlowDecodable : kaldi::DecodableInterface {
    public:
        // DecodableInterface doesn't provide a way to provide more
        // input! Sad!
        virtual float LogLikelihood(int32_t frame, int32_t index);
        virtual bool IsLastFrame(int32_t frame) const;
        virtual int32 NumFramesReady() const;
        virtual int32 NumIndices() const;

        TensorFlowDecodable(const SessionOptions& session_opts);

    private:
        tensorflow::GraphDef graph_;
        std::unique_ptr<tensorflow::Session> session_;
    }

} // end namespace galvASR