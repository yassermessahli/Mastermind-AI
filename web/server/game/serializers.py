from rest_framework import serializers


class StartSerializer(serializers.Serializer):
    mode = serializers.ChoiceField(choices=["codebreaker", "codekeeper"])
    n_colors = serializers.IntegerField(min_value=3, max_value=6)
    n_pegs = serializers.IntegerField(min_value=3, max_value=6)
    max_steps = serializers.IntegerField(min_value=5, max_value=10)


class GuessSerializer(serializers.Serializer):
    guess_idx = serializers.IntegerField(min_value=0)


class FeedbackSerializer(serializers.Serializer):
    blacks = serializers.IntegerField(min_value=0)
    whites = serializers.IntegerField(min_value=0)

    def validate(self, data):
        n_pegs = self.context.get("n_pegs", 6)
        if data["blacks"] > n_pegs:
            raise serializers.ValidationError(f"blacks must be <= {n_pegs}")
        if data["whites"] > n_pegs:
            raise serializers.ValidationError(f"whites must be <= {n_pegs}")
        if data["blacks"] + data["whites"] > n_pegs:
            raise serializers.ValidationError("blacks + whites cannot exceed n_pegs")
        return data
